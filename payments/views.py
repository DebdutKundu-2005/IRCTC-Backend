import uuid


from rest_framework.views import APIView
from rest_framework import status, generics, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema

from .models import Payment
from .serializers import PaymentSerializer
from bookings.tasks import send_booking_confirmation_email


# =========================================================
# PAYMENT PROCESS REQUEST SERIALIZER
# =========================================================

class PaymentProcessRequestSerializer(serializers.Serializer):
    action = serializers.ChoiceField(
        choices=["SUCCESS", "FAILED"]
    )


# =========================================================
# CREATE PAYMENT
# =========================================================

class PaymentCreateView(generics.CreateAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):

        booking = serializer.validated_data["booking"]

        # User can only pay for his own booking
        if booking.user != self.request.user:
            raise serializers.ValidationError(
                "You can only make payment for your own booking."
            )

        # Save payment as PENDING
        serializer.save(
            status="PENDING"
        )


# =========================================================
# PAYMENT SUCCESS
# =========================================================

class PaymentSuccessView(generics.UpdateAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(
            booking__user=self.request.user
        )

    def update(self, request, *args, **kwargs):

        payment = self.get_object()

        # Already successful
        if payment.status == "COMPLETED":
            raise serializers.ValidationError(
                "This payment is already successful."
            )

        # Failed payment cannot become successful
        if payment.status == "FAILED":
            raise serializers.ValidationError(
                "Failed payment cannot be marked as successful."
            )

        # Generate transaction ID
        payment.status = "COMPLETED"

        payment.transaction_id = (
            f"TXN-{uuid.uuid4().hex[:12].upper()}"
        )

        payment.save(
            update_fields=[
                "status",
                "transaction_id",
                "updated_at",
            ]
        )

        # Confirm booking
        booking = payment.booking
        booking.status = "CONFIRMED"

        booking.save(
            update_fields=["status"]
        )

        # Send confirmation email using Celery
        send_booking_confirmation_email.delay(
            booking.id
        )

        return Response(
            {
                "message": "Payment successful.",
                "payment_id": payment.id,
                "booking": booking.id,
                "booking_pnr": booking.pnr,
                "transaction_id": payment.transaction_id,
                "status": payment.status,
            },
            status=status.HTTP_200_OK,
        )


# =========================================================
# PAYMENT FAILED
# =========================================================

class PaymentFailedView(generics.UpdateAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(
            booking__user=self.request.user
        )

    def update(self, request, *args, **kwargs):

        payment = self.get_object()

        # Successful payment cannot be failed
        if payment.status == "COMPLETED":
            raise serializers.ValidationError(
                "Successful payment cannot be marked as failed."
            )

        # Already failed
        if payment.status == "FAILED":
            raise serializers.ValidationError(
                "This payment is already failed."
            )

        # Mark payment failed
        payment.status = "FAILED"

        payment.transaction_id = (
            f"TXN-{uuid.uuid4().hex[:12].upper()}"
        )

        payment.save(
            update_fields=[
                "status",
                "transaction_id",
                "updated_at",
            ]
        )

        # Cancel booking
        booking = payment.booking
        booking.status = "CANCELLED"

        booking.save(
            update_fields=["status"]
        )

        return Response(
            {
                "message": "Payment failed.",
                "payment_id": payment.id,
                "booking": booking.id,
                "booking_pnr": booking.pnr,
                "status": payment.status,
                "transaction_id": payment.transaction_id,
            },
            status=status.HTTP_200_OK,
        )


# =========================================================
# PAYMENT DETAIL
# =========================================================

class PaymentDetailView(generics.RetrieveAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(
            booking__user=self.request.user
        )


# =========================================================
# PAYMENT PROCESS
# =========================================================

class PaymentProcessView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=PaymentProcessRequestSerializer,
        responses={
            200: PaymentSerializer,
        },
    )
    def post(self, request, payment_id):

        # -------------------------------------------------
        # Validate request body
        # -------------------------------------------------

        serializer = PaymentProcessRequestSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        payment_action = serializer.validated_data["action"]

        # -------------------------------------------------
        # Get payment
        # -------------------------------------------------

        try:
         payment = Payment.objects.select_related(
          "booking"
         ).get(
             id=payment_id,
             booking__user= request.user,
) 

        except Payment.DoesNotExist:

            return Response(
                {
                    "error": "Payment not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # -------------------------------------------------
        # Check payment owner
        # -------------------------------------------------

        if payment.booking.user != request.user:

            return Response(
                {
                    "error": (
                        "You can only process your own payment."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # -------------------------------------------------
        # Payment must be PENDING
        # -------------------------------------------------

        if payment.status != "PENDING":

            return Response(
                {
                    "error": (
                        f"Payment is already "
                        f"{payment.status}."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # -------------------------------------------------
        # Generate transaction ID
        # -------------------------------------------------

        transaction_id = (
            f"TXN-{uuid.uuid4().hex[:12].upper()}"
        )

        payment.transaction_id = transaction_id
        if payment_action == "SUCCESS":
            payment.status = "COMPLETED"
        else:
          payment.status = "FAILED"

        payment.save(
            update_fields=[
                "transaction_id",
                "status",
                "updated_at",
            ]
        )

        # -------------------------------------------------
        # SUCCESS
        # -------------------------------------------------

        if payment_action == "SUCCESS":

            payment.booking.status = "CONFIRMED"

            payment.booking.save(
                update_fields=["status"]
            )

            # Send confirmation email through Celery
            send_booking_confirmation_email.delay(
                payment.booking.id
            )

        # -------------------------------------------------
        # FAILED
        # -------------------------------------------------

        elif payment_action == "FAILED":

            payment.booking.status = "CANCELLED"

            payment.booking.save(
                update_fields=["status"]
            )

        # -------------------------------------------------
        # Response
        # -------------------------------------------------

        return Response(
            {
                "message": (
                    f"Payment "
                    f"{payment_action.lower()} successfully."
                ),
                "payment_id": payment.id,
                "booking": payment.booking.id,
                "booking_pnr": payment.booking.pnr,
                "amount": str(payment.amount),
                "payment_method": payment.payment_method,
                "status": payment.status,
                "transaction_id": payment.transaction_id,
            },
            status=status.HTTP_200_OK,
        )