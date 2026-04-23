from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Event, EventAdmin, Management, MeetingRequest, OrganizationAdmin, PaymentRecord, Student, Teacher, UserDirectoryMeta
from .serializers import EventAdminSerializer, MeetingRequestSerializer, OrganizationAdminSerializer, PaymentRecordSerializer, SystemUserSerializer


class EventAdminViewSet(viewsets.ModelViewSet):
    queryset = EventAdmin.objects.all().order_by('-created_at')
    serializer_class = EventAdminSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        search = (self.request.query_params.get('search') or '').strip()
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(email__icontains=search) |
                Q(organization__icontains=search)
            )
        return queryset

    def perform_create(self, serializer):
        event_admin = serializer.save()
        PaymentRecord.objects.create(
            organization=event_admin.organization or '',
            email=event_admin.email,
            role='Event Admin',
            event_admin_id=event_admin.id,
            amount=0,
            due_date=timezone.now().date(),
            status='Pending',
        )


class OrganizationAdminViewSet(viewsets.ModelViewSet):
    queryset = OrganizationAdmin.objects.select_related('management').all().order_by('-id')
    serializer_class = OrganizationAdminSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        search = (self.request.query_params.get('search') or '').strip()
        if search:
            queryset = queryset.filter(
                Q(management__Management_name__icontains=search) |
                Q(email__icontains=search)
            )
        return queryset

    def perform_create(self, serializer):
        org_admin = serializer.save()
        PaymentRecord.objects.create(
            organization=org_admin.management.Management_name if org_admin.management else '',
            email=org_admin.email,
            role='Admin',
            organization_admin=org_admin,
            amount=0,
            due_date=timezone.now().date(),
            status='Pending',
        )

    def perform_update(self, serializer):
        instance = serializer.instance
        management = instance.management
        raw_rfid = self.request.data.get('rfid', None)

        if raw_rfid is None:
            serializer.save()
            return

        if isinstance(raw_rfid, str):
            new_rfids = {item.strip() for item in raw_rfid.split(',') if item.strip()}
        elif isinstance(raw_rfid, list):
            new_rfids = {str(item).strip() for item in raw_rfid if str(item).strip()}
        else:
            raise ValidationError({'rfid': 'RFID must be a comma-separated string or array'})

        students_matching = Student.objects.filter(student_rollNo__in=new_rfids)
        teachers_matching = Teacher.objects.filter(teacher_rollNo__in=new_rfids)
        found_rfids = set(students_matching.values_list('student_rollNo', flat=True)) | set(
            teachers_matching.values_list('teacher_rollNo', flat=True)
        )

        invalid_rfids = sorted(new_rfids - found_rfids)
        if invalid_rfids:
            raise ValidationError({
                'rfid': f'Unknown RFID values: {", ".join(invalid_rfids)}',
                'invalid_rfids': invalid_rfids,
            })

        current_rfids = set(
            Student.objects.filter(management=management).values_list('student_rollNo', flat=True)
        ) | set(
            Teacher.objects.filter(management=management).values_list('teacher_rollNo', flat=True)
        )

        to_remove = current_rfids - new_rfids
        to_add = new_rfids - current_rfids

        with transaction.atomic():
            serializer.save()
            if to_remove:
                Student.objects.filter(
                    management=management,
                    student_rollNo__in=to_remove,
                ).update(management=None)
                Teacher.objects.filter(
                    management=management,
                    teacher_rollNo__in=to_remove,
                ).update(management=None)

            if to_add:
                Student.objects.filter(student_rollNo__in=to_add).update(management=management)
                Teacher.objects.filter(teacher_rollNo__in=to_add).update(management=management)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        management = instance.management

        with transaction.atomic():
            # Removing an org admin must break org ownership links
            # so student/teacher rows no longer point to that management.
            Student.objects.filter(management=management).update(management=None)
            Teacher.objects.filter(management=management).update(management=None)
            instance.delete()

        return Response(status=204)


class SystemUserViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def _default_role(self, kind):
        mapping = {
            'student': 'Student',
            'teacher': 'Teacher',
            'organization_admin': 'Admin',
            'event_admin': 'Event Admin',
        }
        return mapping.get(kind, 'User')

    def _default_department(self, kind, obj):
        if kind == 'student':
            return obj.dept or ''
        if kind == 'teacher':
            programs = [p.strip() for p in (obj.programs or '').split(',') if p.strip()]
            return programs[0] if programs else ''
        return ''

    def _organization_name(self, kind, obj):
        if kind in ('student', 'teacher'):
            management = getattr(obj, 'management', None)
            return management.Management_name if management else ''
        if kind == 'organization_admin':
            management = getattr(obj, 'management', None)
            return management.Management_name if management else ''
        if kind == 'event_admin':
            return obj.organization or ''
        return ''

    def _base_record(self, kind, source_id, name, email, organization, department):
        return {
            'id': f'{kind}-{source_id}',
            'sourceId': source_id,
            'kind': kind,
            'name': name or '',
            'email': email or '',
            'role': self._default_role(kind),
            'organization': organization or '',
            'department': department or '',
            'status': 'offline',
        }

    def _apply_meta(self, record):
        meta = UserDirectoryMeta.objects.filter(
            user_kind=record['kind'],
            source_id=record['sourceId'],
        ).first()
        if meta:
            record['role'] = meta.role
            record['status'] = meta.status
        return record

    def list(self, request):
        users = []

        for s in Student.objects.select_related('management').all():
            users.append(
                self._apply_meta(
                    self._base_record(
                        'student',
                        s.student_id,
                        s.student_name,
                        s.email,
                        self._organization_name('student', s),
                        self._default_department('student', s),
                    )
                )
            )

        for t in Teacher.objects.select_related('management').all():
            users.append(
                self._apply_meta(
                    self._base_record(
                        'teacher',
                        t.teacher_id,
                        t.teacher_name,
                        t.email,
                        self._organization_name('teacher', t),
                        self._default_department('teacher', t),
                    )
                )
            )

        for a in OrganizationAdmin.objects.select_related('management').all():
            users.append(
                self._apply_meta(
                    self._base_record(
                        'organization_admin',
                        a.id,
                        a.management.Management_name if a.management else '',
                        a.email,
                        self._organization_name('organization_admin', a),
                        '',
                    )
                )
            )

        for ea in EventAdmin.objects.all():
            users.append(
                self._apply_meta(
                    self._base_record(
                        'event_admin',
                        ea.id,
                        ea.name,
                        ea.email,
                        self._organization_name('event_admin', ea),
                        '',
                    )
                )
            )

        search = (request.query_params.get('search') or '').strip().lower()
        if search:
            users = [
                u for u in users
                if search in (u['name'] or '').lower() or search in (u['email'] or '').lower()
            ]

        serializer = SystemUserSerializer(users, many=True)
        return Response(serializer.data)

    def partial_update(self, request, pk=None):
        try:
            kind, source_id_str = (pk or '').split('-', 1)
            source_id = int(source_id_str)
        except Exception as exc:
            raise ValidationError({'id': 'Invalid user identifier'}) from exc

        role = request.data.get('role')
        status = request.data.get('status')

        if role is None and status is None:
            raise ValidationError({'detail': 'Provide role and/or status to update'})

        meta, _ = UserDirectoryMeta.objects.get_or_create(
            user_kind=kind,
            source_id=source_id,
            defaults={
                'role': self._default_role(kind),
                'status': 'offline',
            },
        )

        if role is not None:
            meta.role = str(role)
        if status is not None:
            if status not in ('online', 'offline'):
                raise ValidationError({'status': 'Status must be online or offline'})
            meta.status = status
        meta.save()

        return self.retrieve(request, pk=pk)

    def retrieve(self, request, pk=None):
        data = self.list(request).data
        for row in data:
            if row['id'] == pk:
                return Response(row)
        return Response({'detail': 'Not found'}, status=404)

    def destroy(self, request, pk=None):
        try:
            kind, source_id_str = (pk or '').split('-', 1)
            source_id = int(source_id_str)
        except Exception as exc:
            raise ValidationError({'id': 'Invalid user identifier'}) from exc

        if kind == 'organization_admin':
            admin_obj = OrganizationAdmin.objects.filter(id=source_id).first()
            if admin_obj:
                management = admin_obj.management
                Student.objects.filter(management=management).update(management=None)
                Teacher.objects.filter(management=management).update(management=None)
                admin_obj.delete()
        elif kind == 'event_admin':
            event_admin = EventAdmin.objects.filter(id=source_id).first()
            if event_admin:
                Event.objects.filter(event_admin_id=event_admin.id).update(event_admin=None)
                event_admin.delete()
        elif kind == 'student':
            Student.objects.filter(student_id=source_id).delete()
        elif kind == 'teacher':
            Teacher.objects.filter(teacher_id=source_id).delete()
        else:
            raise ValidationError({'kind': 'Unsupported user kind for delete'})

        UserDirectoryMeta.objects.filter(user_kind=kind, source_id=source_id).delete()
        return Response(status=204)


class MeetingRequestViewSet(viewsets.ModelViewSet):
    queryset = MeetingRequest.objects.all().order_by('-created_at')
    serializer_class = MeetingRequestSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        search = (self.request.query_params.get('search') or '').strip()
        if search:
            queryset = queryset.filter(
                Q(organization__icontains=search) |
                Q(email__icontains=search) |
                Q(role__icontains=search) |
                Q(purpose__icontains=search)
            )
        return queryset

    def partial_update(self, request, *args, **kwargs):
        allowed = {'date', 'time', 'status'}
        invalid = [key for key in request.data.keys() if key not in allowed]
        if invalid:
            raise ValidationError({'detail': f'Only date, time and status can be updated. Invalid fields: {", ".join(invalid)}'})
        return super().partial_update(request, *args, **kwargs)


class PaymentRecordViewSet(viewsets.ModelViewSet):
    queryset = PaymentRecord.objects.all().order_by('-created_at')
    serializer_class = PaymentRecordSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        search = (self.request.query_params.get('search') or '').strip()
        if search:
            queryset = queryset.filter(
                Q(organization__icontains=search) |
                Q(email__icontains=search) |
                Q(role__icontains=search)
            )
        return queryset

    def partial_update(self, request, *args, **kwargs):
        allowed = {'amount', 'dueDate', 'status'}
        invalid = [key for key in request.data.keys() if key not in allowed]
        if invalid:
            raise ValidationError({'detail': f'Only amount, dueDate and status can be updated. Invalid fields: {", ".join(invalid)}'})
        return super().partial_update(request, *args, **kwargs)

    def perform_create(self, serializer):
        role = (self.request.data.get('role') or '').strip().lower()
        email = (self.request.data.get('email') or '').strip()
        organization = (self.request.data.get('organization') or '').strip()

        organization_admin = None
        event_admin = None

        if role == 'admin':
            organization_admin = OrganizationAdmin.objects.filter(
                email__iexact=email,
                management__Management_name__iexact=organization,
            ).first()
            if organization_admin is None:
                organization_admin = OrganizationAdmin.objects.filter(email__iexact=email).first()
        elif role == 'event admin':
            event_admin = EventAdmin.objects.filter(
                email__iexact=email,
                organization__iexact=organization,
            ).first()
            if event_admin is None:
                event_admin = EventAdmin.objects.filter(email__iexact=email).first()

        serializer.save(
            organization_admin=organization_admin,
            event_admin=event_admin,
        )
