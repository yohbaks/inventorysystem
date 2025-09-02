# signals.py

import qrcode
from io import BytesIO
from django.core.files import File
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from .models import Desktop_Package

# This signal will generate a QR code when a new Desktop_Package instance is created
@receiver(post_save, sender=Desktop_Package)
def generate_qr_code(sender, instance, created, **kwargs):
    if created and not instance.qr_code:
        # Build full URL for this desktop package
        url = reverse('desktop_details_view', kwargs={'package_id': instance.pk})
        full_url = f"http://127.0.0.1:8000{url}"  # Replace with your domain in production

        # Generate the QR code image
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(full_url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        # Save QR code image into the model
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        filename = f'desktop_qr_{instance.pk}.png'

        instance.qr_code.save(filename, File(buffer), save=False)
        instance.save(update_fields=['qr_code'])  # Save only the qr_code field
