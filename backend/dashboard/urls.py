from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import EventAdminViewSet, OrganizationAdminViewSet

router = DefaultRouter()
router.register(r'events/event-admins', EventAdminViewSet, basename='event-admin')
router.register(r'organization-admins', OrganizationAdminViewSet, basename='organization-admin')

urlpatterns = [
    path('', include(router.urls)),
]
