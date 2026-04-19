from django.db import models


class Management(models.Model):
    Management_id = models.AutoField(primary_key=True)
    Management_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True, null=True, blank=True)

    class Meta:
        db_table = 'core_management'
        managed = False


class Student(models.Model):
    student_id = models.AutoField(primary_key=True)
    student_rollNo = models.CharField(max_length=100, unique=True)
    management = models.ForeignKey(
        Management,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students',
    )

    class Meta:
        db_table = 'core_student'
        managed = False


class Teacher(models.Model):
    teacher_id = models.AutoField(primary_key=True)
    teacher_rollNo = models.CharField(max_length=100, unique=True)
    management = models.ForeignKey(
        Management,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='teachers',
    )

    class Meta:
        db_table = 'core_teacher'
        managed = False


class EventAdmin(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]

    name = models.CharField(max_length=200)
    email = models.EmailField()
    organization = models.CharField(max_length=255)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField()

    class Meta:
        db_table = 'event_admin'
        managed = False


class Event(models.Model):
    title = models.CharField(max_length=200)
    event_date = models.DateField(null=True, blank=True)
    start_time = models.DateTimeField(null=True, blank=True)
    event_admin = models.ForeignKey(
        EventAdmin,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_events',
    )

    class Meta:
        db_table = 'events_event'
        managed = False


class OrganizationAdmin(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]

    management = models.OneToOneField(
        Management,
        on_delete=models.CASCADE,
        related_name='organization_admin',
    )
    email = models.EmailField(unique=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'organization_admin'

