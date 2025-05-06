from rest_framework import generics, status
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.views import APIView

from .models import Application
from django.db import models
from .serializers import ApplicationSerializer, MeetingRequestSerializer

class ApplicationCreateAPIView(generics.CreateAPIView):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer

    def perform_create(self, serializer):
        instance = serializer.save(status='RECEIVED')

        # Email to user
        user_message = (
            f"Hi {instance.full_name},\n\n"
            f"Thanks for submitting your project idea. We'll get back to you shortly.\n\n"
            f"Project: {instance.project_name}\n"
            f"Status: {instance.status}\n\n"
            f"Regards,\nYour Company"
        )
        send_mail(
            subject="Thank you for your submission!",
            message=user_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.email],
            fail_silently=False
        )

        # Email to admin
        admin_message = (
            f"New client request submitted.\n\n"
            f"Name: {instance.full_name}\n"
            f"Email: {instance.email}\n"
            f"Project: {instance.project_name}\n\n"
            f"View in admin panel."
        )
        send_mail(
            subject=f"New Client Request: {instance.full_name}",
            message=admin_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.DEFAULT_FROM_EMAIL],
            fail_silently=False
        )

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class RequestMeetingAPIView(APIView):
    def post(self, request):
        serializer = MeetingRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        app = Application.objects.filter(models.Q(email=email) | models.Q(office_email=email)).first()

        # Mail to admin
        admin_msg = (
            f"The client '{app.full_name}' has requested a meeting.\n\n"
            f"Email: {email}\n"
            f"Project: {app.project_name}\n\n"
            f"Please respond with a meeting link."
        )
        send_mail(
            subject=f"Meeting Request: {app.full_name}",
            message=admin_msg,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.DEFAULT_FROM_EMAIL],
            fail_silently=True
        )

        # Mail to user
        user_msg = (
            f"Hi {app.full_name},\n\n"
            f"We've received your request for a meeting.\n"
            f"Our team will review it and get back to you soon with a meeting link.\n\n"
            f"Thanks,\nYour Company"
        )
        send_mail(
            subject="Meeting Request Received",
            message=user_msg,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False
        )

        return Response({"message": "Meeting request submitted successfully."}, status=200)
