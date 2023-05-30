from django.contrib.auth import authenticate, login, logout
from django.contrib.sessions.models import Session
from django.utils.crypto import get_random_string
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(request, username=username, password=password)

    if user is not None:
        login(request, user)
        token = Token.objects.get_or_create(user=user)[0].key

        return Response({'token':'Token ' + token}, status=200)
    else:
        return Response({'error': 'نام کاربری یا رمز عبور اشتباه است!'}, status=400)


@api_view(['POST'])
def logout_view(request):
    logout(request)
    return Response(status=200)
