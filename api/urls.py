from django.urls import path
from .views import get_user_role,register_user,register, login, add_train, get_seat_availability, book_seat, get_booking_details

urlpatterns = [
    path('register/', register),
    path('login/', login),
    path('add_train/', add_train),
    path('trains/<int:train_id>/seats/', get_seat_availability),
    path('book_seat/', book_seat),
    path('booking/<int:booking_id>/', get_booking_details),
    path('register/', register_user, name='register_user'),
    path('user/', get_user_role, name='get_user_role'),
]
