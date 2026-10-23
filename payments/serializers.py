from rest_framework import serializers
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    booking_pnr = serializers.CharField(
        source='booking.pnr',
        read_only=True
    )

    class Meta:
        model = Payment
        fields = [
            'id',
            'booking',
            'booking_pnr',
            'amount',
            'payment_method',
            'status',
            'transaction_id',
            'created_at',
            'updated_at',
        ]

        read_only_fields = [
            'id',
            'booking_pnr',
            'status',
            'transaction_id',
            'created_at',
            'updated_at',
        ]

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Payment amount must be greater than 0."
            )

        return value

   
   
    def validate(self, data):
        booking = data.get('booking')
        amount = data.get('amount')

        if booking is not None:
            if Payment.objects.filter(booking=booking).exists():
                raise serializers.ValidationError({
                "booking": "Payment already exists for this booking."
            })

            if booking.status == 'CANCELLED':
                raise serializers.ValidationError({
                "booking": "Payment cannot be created for a cancelled booking."
            })

        # Verify payment amount against the saved booking fare
            if amount is not None and amount != booking.fare_amount:
                raise serializers.ValidationError({
                    "amount": (
                        f"Payment amount must match the booking fare "
                        f"of ₹{booking.fare_amount}."
                    )
                })

        return data
