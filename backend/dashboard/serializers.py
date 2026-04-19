from django.db.models import Q
from django.utils import timezone
from rest_framework import serializers

from .models import EventAdmin, Event, Management, OrganizationAdmin, Student, Teacher


class EventAdminSerializer(serializers.ModelSerializer):
    eventsManaged = serializers.SerializerMethodField()
    activeEvents = serializers.SerializerMethodField()
    joinDate = serializers.DateTimeField(source='created_at', format='%Y-%m-%d', read_only=True)

    class Meta:
        model = EventAdmin
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

    def get_eventsManaged(self, obj):
        return Event.objects.filter(event_admin_id=obj.id).count()

    def get_activeEvents(self, obj):
        now = timezone.now()
        today = now.date()
        return Event.objects.filter(
            event_admin_id=obj.id
        ).filter(
            Q(event_date__gte=today) | Q(start_time__gte=now)
        ).count()


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
