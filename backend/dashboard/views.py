from django.db import transaction
from django.db.models import Q
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny

from .models import EventAdmin, OrganizationAdmin, Student, Teacher
from .serializers import EventAdminSerializer, OrganizationAdminSerializer


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
            raise ValidationError({'rfid': f'Unknown RFID values: {", ".join(invalid_rfids)}'})

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
