from django.urls import path
from .views import (
    BookingListCreateView,
    PassengerListCreateView,
    BookingDetailView,
    PNRSearchView,
    BookingCancelView,
)

urlpatterns = [
    path('', BookingListCreateView.as_view(), name='booking-list-create'),

    path(
        '<int:booking_id>/passengers/',
        PassengerListCreateView.as_view(),
        name='passenger-list-create'
    ),

    path(
        '<int:pk>/',
        BookingDetailView.as_view(),
        name='booking-detail'
    ),
    path('pnr/<str:pnr>/', PNRSearchView.as_view(), name='pnr-search'),
    path(
    '<int:pk>/cancel/',
    BookingCancelView.as_view(),
    name='booking-cancel'
    ),
]