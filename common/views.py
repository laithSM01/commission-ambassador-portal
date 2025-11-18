from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import exceptions

from core.models import User
from .authentication import JWTAuthentication
from .serializers import UserSerializer

class RegisterAPIView(APIView):
    def post(self, request):
        data = request.data

        if data['password'] != data['password_confirm']:
            raise exceptions.APIException('Passwords do not match!')

        data['is_ambassador'] = 'api/ambassador' in request.path #added after creating ambassador app
        # data['is_ambassador'] = 0 before creating ambassador app

        serializer = UserSerializer(data=data)
        serializer.is_valid(raise_exception=True) # validate the data validation layer
        serializer.save()
        return Response(serializer.data)

class LoginAPIView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = User.objects.filter(email=email).first()

        if user is None:
            raise exceptions.AuthenticationFailed('User not found!')

        if not user.check_password(password):
            raise exceptions.APIException('Invalid password!')

        scope = 'ambassador' if 'api/ambassador' in request.path else 'admin'

        print("i want to see scope : ",scope)
        print("i want to see is_ambassador : ", user.is_ambassador)

        if user.is_ambassador and scope =='admin':
            raise exceptions.AuthenticationFailed('ambassador cant login in admin mode!')

        token = JWTAuthentication.generate_token(user.id, scope)

        response = Response()
        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {
            'message': 'Login success',
        }

        return response

class UserAPIView(APIView):

    # our authentication class is what we created in authentication.py because it handles JWT tokens
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        data = UserSerializer(request.user).data
        if 'api/ambassador' in request.path:
            data['revenue'] = user.revenue
        return Response(data)

class LogoutAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self, _):
        response = Response()
        response.delete_cookie(key='jwt')
        response.data = {
            'message': 'Logout success',
        }
        return response

class ProfileInfoAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request, pk=None):
        user = request.user
        # the request will have the data to update the user
        serializer = UserSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class ProfilePasswordAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def put(self, request, pk=None):
        user = request.user
        data = request.data

        if data['password'] != data['password_confirm']:
            raise exceptions.APIException('Passwords do not match!')
        user.set_password(data['password'])
        user.save()
        return Response(UserSerializer(user).data)
