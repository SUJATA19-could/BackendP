from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.db import models

from .models import Application
from .serializers import ApplicationSerializer, MeetingRequestSerializer


def send_email(subject, message, recipient, html_message=None, fail_silently=False):
    email = EmailMultiAlternatives(
        subject=subject,
        body=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient]
    )
    if html_message:
        email.attach_alternative(html_message, "text/html")
    email.send(fail_silently=fail_silently)


class ApplicationCreateAPIView(generics.CreateAPIView):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer

    def perform_create(self, serializer):
        email = serializer.validated_data.get("email")
        if Application.objects.filter(email=email).exists():
            raise Exception("An application with this email already exists.")

        instance = serializer.save(status='RECEIVED')

        # Filter fields to include in user summary
        excluded_fields = {'id', 'created_at', 'updated_at', 'status', 'progress_details'}
        included_fields = [field for field in serializer.fields.keys() if field not in excluded_fields]

        user_data = "\n".join([
            f"{field.replace('_', ' ').title()}: {getattr(instance, field)}"
            for field in included_fields
        ])

        # Email to user (Plain + HTML)
        subject_user = "Thank you for your submission!"
        text_user = (
            f"Hi {instance.full_name},\n\n"
            f"Thanks for submitting your project idea. Here's a copy of what you submitted:\n\n"
            f"{user_data}\n\n"
            f"Status: {instance.status}\n\n"
            f"Regards,\nYour Company"
        )
        html_user = f"""
        <p>Hi <strong>{instance.full_name}</strong>,</p>
        <p>Thanks for submitting your project idea. Here's a copy of what you submitted:</p>
        <pre>{user_data}</pre>
        <p><strong>Status:</strong> {instance.status}</p>
        <p>Regards,<br>Your Company</p>
        """

        send_email(subject_user, text_user, instance.email, html_message=html_user)

        # Email to admin
        subject_admin = f"New Client Request: {instance.full_name}"
        text_admin = (
            f"New client request submitted.\n\n"
            f"Name: {instance.full_name}\n"
            f"Email: {instance.email}\n"
            f"Project: {instance.project_name}\n\n"
            f"View in admin panel."
        )
        send_email(subject_admin, text_admin, settings.DEFAULT_FROM_EMAIL)

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

        app = Application.objects.filter(
            models.Q(email=email) | models.Q(office_email=email)
        ).first()

        if not app:
            return Response({"error": "No application found for this email."}, status=404)

        # Update meeting flag
        app.requested_meeting = True
        app.save(update_fields=['requested_meeting'])

        # Email to admin
        subject_admin = f"Meeting Request: {app.full_name}"
        text_admin = (
            f"The client '{app.full_name}' has requested a meeting.\n\n"
            f"Email: {email}\n"
            f"Project: {app.project_name}\n\n"
            f"Please respond with a meeting link."
        )
        send_email(subject_admin, text_admin, settings.DEFAULT_FROM_EMAIL, fail_silently=True)

        # Email to user
        subject_user = "Meeting Request Received"
        text_user = (
            f"Hi {app.full_name},\n\n"
            f"We've received your request for a meeting regarding your project: {app.project_name}.\n"
            f"Our team will review it and get back to you soon with a meeting link.\n\n"
            f"Thanks,\nYour Company"
        )
        html_user = f"""
        <p>Hi <strong>{app.full_name}</strong>,</p>
        <p>We've received your meeting request for your project: <strong>{app.project_name}</strong>.</p>
        <p>Our team will review it and respond shortly with a meeting link.</p>
        <p>Thanks,<br>Your Company</p>
        """
        send_email(subject_user, text_user, email, html_message=html_user)

        return Response({"message": "Meeting request submitted successfully."}, status=200)
