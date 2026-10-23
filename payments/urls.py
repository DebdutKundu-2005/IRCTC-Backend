from django.urls import path

from .views import (
    PaymentCreateView,
    PaymentProcessView,
    PaymentSuccessView,
    PaymentFailedView,
    PaymentDetailView,
)


urlpatterns = [
    path(
        '',
        PaymentCreateView.as_view(),
        name='payment-create'
    ),

    path(
        '<int:pk>/success/',
        PaymentSuccessView.as_view(),
        name='payment-success'
    ),

    path(
        '<int:pk>/failed/',
        PaymentFailedView.as_view(),
        name='payment-failed'
    ),
    path(
    '<int:pk>/',
    PaymentDetailView.as_view(),
    name='payment-detail'
   ),
   path(
        "<int:payment_id>/process/",
        PaymentProcessView.as_view(),
        name="payment-process"
    ),
]