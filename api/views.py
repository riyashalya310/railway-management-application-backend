from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.db import transaction
from .models import User, Train, Booking
from .serializers import UserSerializer, TrainSerializer, BookingSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.conf import settings

ADMIN_API_KEY = 'your_admin_api_key'

@api_view(['POST'])
def register(request):
    data = request.data
    user = User.objects.create_user(
        username=data['username'],
        password=data['password'],
        role=data['role']
    )
    serializer = UserSerializer(user)
    return Response(serializer.data)

@api_view(['POST'])
def login(request):
    data = request.data
    user = authenticate(username=data['username'], password=data['password'])
    if user:
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })
    return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
def add_train(request):
    api_key = request.headers.get('Api-Key')
    if api_key != ADMIN_API_KEY:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
    
    data = request.data
    serializer = TrainSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_seat_availability(request, train_id):
    try:
        train = Train.objects.get(id=train_id)
    except Train.DoesNotExist:
        return Response({'error': 'Train not found'}, status=status.HTTP_404_NOT_FOUND)
    
    booked_seats = Booking.objects.filter(train=train).count()
    available_seats = train.total_seats - booked_seats
    return Response({'available_seats': available_seats})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def book_seat(request):
    data = request.data
    train = Train.objects.get(id=data['train_id'])
    
    with transaction.atomic():
        booked_seats = Booking.objects.filter(train=train).count()
        if booked_seats >= train.total_seats:
            return Response({'message': 'No seats available'}, status=status.HTTP_400_BAD_REQUEST)
        
        new_booking = Booking(
            user=request.user,
            train=train,
            seat_number=booked_seats + 1
        )
        new_booking.save()
    
    serializer = BookingSerializer(new_booking)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_booking_details(request, booking_id):
    try:
        booking = Booking.objects.get(id=booking_id, user=request.user)
    except Booking.DoesNotExist:
        return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = BookingSerializer(booking)
    return Response(serializer.data)


@api_view(['POST'])
def register_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        if user:
            return Response(status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_role(request):
    user = request.user
    return Response({'role': user.role})