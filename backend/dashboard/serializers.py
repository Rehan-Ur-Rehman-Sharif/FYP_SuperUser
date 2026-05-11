from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone
from rest_framework import serializers

from .models import Event, EventAdvisor, Management, MeetingRequest, OrganizationAdmin, PaymentRecord, Student, Teacher, UserDirectoryMeta

User = get_user_model()


class EventAdvisorSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True, required=False)
    organization = serializers.CharField(required=False, allow_blank=True, write_only=True)
    eventsManaged = serializers.SerializerMethodField()
    activeEvents = serializers.SerializerMethodField()
    joinDate = serializers.DateTimeField(source='created_at', format='%Y-%m-%d', read_only=True)
    status = serializers.SerializerMethodField()

    class Meta:
        model = EventAdvisor
        fields = [
            'id',
            'name',
            'email',
            'organization',
            'status',
            'eventsManaged',
            'activeEvents',
            'joinDate',
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['email'] = (instance.user.email or '').strip() if getattr(instance, 'user_id', None) else ''
        data['organization'] = ''
        return data

    def _account_meta(self, obj):
        return UserDirectoryMeta.objects.filter(
            user_kind='event_advisor',
            source_id=obj.id,
        ).first()

    def get_status(self, obj):
        meta = self._account_meta(obj)
        if meta:
            return meta.account_status or 'active'
        return 'active'

    def get_eventsManaged(self, obj):
        uid = getattr(obj, 'user_id', None)
        if uid is None:
            return 0
        return Event.objects.filter(organiser_id=uid).count()

    def get_activeEvents(self, obj):
        uid = getattr(obj, 'user_id', None)
        if uid is None:
            return 0
        now = timezone.now()
        today = now.date()
        return Event.objects.filter(organiser_id=uid).filter(
            Q(event_date__gte=today) | Q(start_time__gte=now)
        ).count()

    def create(self, validated_data):
        validated_data.pop('organization', None)
        email = (self.initial_data.get('email') or '').strip()
        name = (validated_data.get('name') or '').strip()
        if not email:
            raise serializers.ValidationError({'email': 'This field is required'})
        if not name:
            raise serializers.ValidationError({'name': 'This field is required'})

        user, _created = User.objects.get_or_create(
            username=email,
            defaults={
                'email': email,
                'first_name': name.split()[0] if name else '',
            },
        )
        if user.email != email:
            user.email = email
            user.save(update_fields=['email'])

        if EventAdvisor.objects.filter(user_id=user.id).exists():
            raise serializers.ValidationError({'email': 'An event advisor already exists for this email'})

        return EventAdvisor.objects.create(user=user, name=name)

    def update(self, instance, validated_data):
        validated_data.pop('organization', None)
        email = self.initial_data.get('email')
        if email is not None:
            email = email.strip()
            if email:
                if User.objects.filter(username=email).exclude(pk=instance.user_id).exists():
                    raise serializers.ValidationError({'email': 'This email is already in use'})
                u = instance.user
                u.username = email
                u.email = email
                u.save(update_fields=['username', 'email'])

        status = self.initial_data.get('status')
        if status is not None:
            if status not in ('active', 'inactive'):
                raise serializers.ValidationError({'status': 'Must be active or inactive'})
            meta, _ = UserDirectoryMeta.objects.get_or_create(
                user_kind='event_advisor',
                source_id=instance.id,
                defaults={
                    'role': 'Event Admin',
                    'status': 'offline',
                    'account_status': status,
                },
            )
            meta.account_status = status
            meta.save(update_fields=['account_status', 'updated_at'])

        name = validated_data.get('name')
        if name is not None:
            instance.name = name
            instance.save(update_fields=['name'])

        return instance


class OrganizationAdminSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='management.Management_name', read_only=True)
    organization = serializers.CharField(source='management.Management_name', read_only=True)
    rfid = serializers.SerializerMethodField()
    management_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = OrganizationAdmin
        fields = [
            'id',
            'name',
            'organization',
            'email',
            'status',
            'rfid',
            'management_id',
        ]

    def get_rfid(self, obj):
        student_ids = list(
            Student.objects.filter(management=obj.management)
            .values_list('student_rollNo', flat=True)
        )
        teacher_ids = list(
            Teacher.objects.filter(management=obj.management)
            .values_list('teacher_rollNo', flat=True)
        )
        return sorted([rfid for rfid in (student_ids + teacher_ids) if rfid])

    def create(self, validated_data):
        management_id = validated_data.pop('management_id', None)
        request = self.context.get('request')
        if management_id:
            try:
                management = Management.objects.get(Management_id=management_id)
            except Management.DoesNotExist as exc:
                raise serializers.ValidationError({'management_id': 'Invalid management id'}) from exc
        else:
            management_name = (request.data.get('organization') or request.data.get('name') or '').strip()
            if not management_name:
                raise serializers.ValidationError({'organization': 'Organization name is required'})
            management = Management.objects.filter(Management_name=management_name).first()
            if management is None:
                management = Management.objects.create(
                    Management_name=management_name,
                    email=validated_data.get('email'),
                )

        if OrganizationAdmin.objects.filter(management=management).exists():
            raise serializers.ValidationError({'organization': 'This organization already has an admin'})

        return OrganizationAdmin.objects.create(management=management, **validated_data)


class SystemUserSerializer(serializers.Serializer):
    id = serializers.CharField()
    sourceId = serializers.IntegerField()
    kind = serializers.CharField()
    name = serializers.CharField()
    email = serializers.CharField(allow_blank=True, allow_null=True)
    role = serializers.CharField()
    organization = serializers.CharField(allow_blank=True, allow_null=True)
    department = serializers.CharField(allow_blank=True, allow_null=True)
    status = serializers.ChoiceField(choices=['online', 'offline'])


class MeetingRequestSerializer(serializers.ModelSerializer):
    date = serializers.DateField(source='preferred_date')
    time = serializers.TimeField(source='preferred_time', format='%H:%M', input_formats=['%H:%M', '%H:%M:%S'])

    class Meta:
        model = MeetingRequest
        fields = [
            'id',
            'organization',
            'email',
            'role',
            'purpose',
            'date',
            'time',
            'status',
        ]


class PaymentRecordSerializer(serializers.ModelSerializer):
    dueDate = serializers.DateField(source='due_date')

    class Meta:
        model = PaymentRecord
        fields = [
            'id',
            'organization',
            'email',
            'role',
            'amount',
            'dueDate',
            'status',
        ]
