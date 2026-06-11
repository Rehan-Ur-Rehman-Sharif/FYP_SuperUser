from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import EventAdvisorViewSet, MeetingRequestViewSet, OrganizationAdminViewSet, PaymentRecordViewSet, SystemUserViewSet, dashboard_stats_view

router = DefaultRouter()
router.register(r'events/event-advisors', EventAdvisorViewSet, basename='event-advisor')
router.register(r'organization-admins', OrganizationAdminViewSet, basename='organization-admin')
router.register(r'users', SystemUserViewSet, basename='system-user')
router.register(r'meetings', MeetingRequestViewSet, basename='meeting-request')
router.register(r'payments', PaymentRecordViewSet, basename='payment-record')

urlpatterns = [
    path('stats/', dashboard_stats_view, name='dashboard-stats'),
    path('', include(router.urls)),
]

