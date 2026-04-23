from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import EventAdminViewSet, MeetingRequestViewSet, OrganizationAdminViewSet, PaymentRecordViewSet, SystemUserViewSet

router = DefaultRouter()
router.register(r'events/event-admins', EventAdminViewSet, basename='event-admin')
router.register(r'organization-admins', OrganizationAdminViewSet, basename='organization-admin')
router.register(r'users', SystemUserViewSet, basename='system-user')
router.register(r'meetings', MeetingRequestViewSet, basename='meeting-request')
router.register(r'payments', PaymentRecordViewSet, basename='payment-record')

urlpatterns = [
    path('', include(router.urls)),
]
