from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('waslaa_telecom.apps.users.urls', namespace='users')),
    path('api/plans/', include('waslaa_telecom.apps.plans.urls', namespace='plans')),
    path('api/subscriptions/', include('waslaa_telecom.apps.subscriptions.urls', namespace='subscriptions')),
    path('api/payments/', include('waslaa_telecom.apps.payments.urls', namespace='payments')),
    path('api/tickets/', include('waslaa_telecom.apps.tickets.urls', namespace='tickets')),
]