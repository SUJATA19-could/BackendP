from django.urls import path
from .views import ApplicationCreateAPIView, RequestMeetingAPIView, ContactUsAPIView

urlpatterns = [
    path('create-application', ApplicationCreateAPIView.as_view(), name='create_application'),
    path('request-meeting', RequestMeetingAPIView.as_view(), name='request_meeting'),
	path('contact-us', ContactUsAPIView.as_view(), name='contact_us')
]
