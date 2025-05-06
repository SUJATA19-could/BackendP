from django.contrib import admin, messages
from django.core.mail import send_mail
from django.conf import settings
from .models import Application

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = [
        'full_name', 'email', 'project_name',
        'status', 'meeting_link', 'created_at'
    ]

    list_filter = [
        'status', 'preferred_contact', 'version_needed',
        'approx_users', 'selling_to', 'project_type', 'industry',
        'created_at'
    ]

    search_fields = [
        'email', 'office_email', 'phone', 'whatsapp',
        'project_name', 'full_name', 'budget', 'timeline',
        'other_project_type', 'other_industry', 'description'
    ]

    readonly_fields = ['created_at', 'updated_at']

    fields = [
        'project_name', 'description', 'project_type', 'other_project_type',
        'industry', 'other_industry', 'selling_to', 'approx_users',
        'version_needed', 'budget', 'timeline',
        'full_name', 'email', 'office_email', 'phone', 'whatsapp',
        'preferred_contact', 'requested_meeting', 'meeting_link',
        'status', 'progress_details', 'created_at', 'updated_at'
    ]

    actions = []

    def save_model(self, request, obj, form, change):
        original = None
        if change:
            original = Application.objects.get(pk=obj.pk)

        super().save_model(request, obj, form, change)

        if (
            obj.meeting_link and
            obj.status in ["RECEIVED", "MEETING_REQUESTED"]
        ):
            msg = (
                f"Hi {obj.full_name},\n\n"
                f"Here's your meeting link:\n\n"
                f"{obj.meeting_link}\n\n"
                f"Looking forward to the meeting!\n\n"
                f"Cheers,\nYour Company"
            )

            send_mail(
                subject="Your Meeting Link",
                message=msg,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[obj.email],
                fail_silently=False
            )

            obj.status = "MEETING_SENT"
            obj.save()

            self.message_user(
                request,
                "Meeting link sent automatically after save ✅",
                level=messages.SUCCESS
            )
