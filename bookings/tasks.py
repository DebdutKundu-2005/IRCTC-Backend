from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

from .models import Booking


@shared_task
def send_booking_confirmation_email(booking_id):
    booking = Booking.objects.get(id=booking_id)

    send_mail(
        subject=f"Booking Confirmed - PNR {booking.pnr}",
        message=(
            f"Your railway booking has been confirmed.\n\n"
            f"PNR: {booking.pnr}\n"
            f"Train: {booking.train.train_number} - {booking.train.train_name}\n"
            f"Journey Date: {booking.journey_date}\n"
            f"Passengers: {booking.total_passengers}\n"
            f"Status: {booking.status}\n"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[booking.user.email],
        fail_silently=False,
    )

    return f"Confirmation email sent for PNR {booking.pnr}"