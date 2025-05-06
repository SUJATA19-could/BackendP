from django.urls import path
from .views import ApplicationCreateAPIView, RequestMeetingAPIView

urlpatterns = [
    path('create-application', ApplicationCreateAPIView.as_view(), name='create_application'),
    path('request-meeting', RequestMeetingAPIView.as_view(), name='request_meeting'),
]
