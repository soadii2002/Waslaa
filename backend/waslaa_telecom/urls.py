from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # API
    path('api/users/', include('waslaa_telecom.apps.users.urls', namespace='users')),
    path('api/plans/', include('waslaa_telecom.apps.plans.urls', namespace='plans')),
    path('api/subscriptions/', include('waslaa_telecom.apps.subscriptions.urls', namespace='subscriptions')),
    path('api/payments/', include('waslaa_telecom.apps.payments.urls', namespace='payments')),
    path('api/tickets/', include('waslaa_telecom.apps.tickets.urls', namespace='tickets')),
    path('api/analytics/', include('waslaa_telecom.apps.analytics.urls', namespace='analytics')),
    path('api/announcements/', include('waslaa_telecom.apps.announcements.urls', namespace='announcements')),

    # Swagger
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]