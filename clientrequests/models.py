from django.db import models

class Application(models.Model):
    PROGRESS_CHOICES = [
        ('RECEIVED', 'Received'),
        ('MEETING_REQUESTED', 'Meeting Requested'),
        ('MEETING_SENT', 'Meeting Link Sent'),
        ('IN_DISCUSSION', 'In Discussion'),
        ('IN_PROGRESS', 'In Progress'),
        ('HALTED', 'Halted'),
        ('CLOSED', 'Closed'),
    ]

    # --- Project Information ---
    project_name = models.CharField(max_length=255)
    description = models.TextField(help_text="Minimum 50 characters.")
    project_type = models.CharField(max_length=100)
    other_project_type = models.CharField(max_length=100, blank=True, null=True)
    industry = models.CharField(max_length=100)
    other_industry = models.CharField(max_length=100, blank=True, null=True)
    selling_to = models.CharField(
        max_length=30,
        choices=[
            ('individual', 'Individual Users'),
            ('organization', 'Organizations'),
            ('both', 'Both')
        ]
    )
    approx_users = models.CharField(
        max_length=30,
        choices=[
            ('upto_100', 'Up to 100'),
            ('100_1000', '100–1,000'),
            ('1000_10000', '1,000–10,000'),
            ('10000_100000', '10,000–100,000'),
            ('100000_plus', '100,000+'),
        ]
    )
    version_needed = models.CharField(
        max_length=50,
        choices=[
            ('mvp', 'MVP'),
            ('full', 'Fully Featured Solution'),
            ('both', 'Both'),
        ]
    )
    budget = models.CharField(max_length=100)
    timeline = models.CharField(max_length=100, blank=True, null=True)

    # --- Client Info ---
    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    office_email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    whatsapp = models.CharField(max_length=20, blank=True, null=True)
    preferred_contact = models.CharField(
        max_length=20,
        choices=[
            ('phone', 'Phone'),
            ('whatsapp', 'WhatsApp'),
            ('email', 'Email'),
        ]
    )

    # --- Application Status & Meta ---
    requested_meeting = models.BooleanField(default=False)
    meeting_link = models.URLField(blank=True, null=True)
    status = models.CharField(
        max_length=30,
        choices=PROGRESS_CHOICES,
        default='RECEIVED'
    )
    progress_details = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.project_name} - {self.full_name}"
