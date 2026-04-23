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
    student_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True, null=True, blank=True)
    student_rollNo = models.CharField(max_length=100, unique=True)
    dept = models.CharField(max_length=100)
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
    teacher_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True, null=True, blank=True)
    teacher_rollNo = models.CharField(max_length=100, unique=True)
    programs = models.CharField(max_length=255, blank=True, default='')
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


class UserDirectoryMeta(models.Model):
    STATUS_CHOICES = [
        ('online', 'Online'),
        ('offline', 'Offline'),
    ]

    user_kind = models.CharField(max_length=50)
    source_id = models.PositiveIntegerField()
    role = models.CharField(max_length=50)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='offline')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'dashboard_user_meta'
        unique_together = ('user_kind', 'source_id')


class MeetingRequest(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    organization = models.CharField(max_length=255)
    email = models.EmailField()
    role = models.CharField(max_length=100)
    purpose = models.TextField()
    preferred_date = models.DateField()
    preferred_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'dashboard_meeting_request'


class PaymentRecord(models.Model):
    STATUS_CHOICES = [
        ('Paid', 'Paid'),
        ('Pending', 'Pending'),
        ('Overdue', 'Overdue'),
    ]

    organization = models.CharField(max_length=255)
    email = models.EmailField()
    role = models.CharField(max_length=100)
    organization_admin = models.ForeignKey(
        'OrganizationAdmin',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments',
    )
    event_admin = models.ForeignKey(
        'EventAdmin',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments',
        db_constraint=False,
    )
    amount = models.PositiveIntegerField()
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'dashboard_payment_record'
