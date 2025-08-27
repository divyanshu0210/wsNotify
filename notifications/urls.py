from django.urls import path
from .views import *

urlpatterns = [
    path('create/', create_notification),
    path('pending/', get_pending_notifications),
    path('sent/', get_sent_notifications),
    path('get-sent-count/',get_sent_notifications_count),
    path('mark-as-viewed/',mark_notifications_as_viewed),
]
