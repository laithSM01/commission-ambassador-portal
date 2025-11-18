import jwt, datetime
from rest_framework import exceptions, request
from rest_framework.authentication import BaseAuthentication

from app import settings
from core.models import User


class JWTAuthentication(BaseAuthentication):

    def authenticate(self, request):
        token =request.COOKIES.get('jwt')
        is_ambassador = 'api/ambassador' in request.path
        if not token:
            return None
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignature:
            raise exceptions.AuthenticationFailed('Token Expired')

        if (is_ambassador and payload['scope'] != 'ambassador') or (not is_ambassador and payload['scope'] != 'admin'):
            raise exceptions.AuthenticationFailed('Invalid scope')

        user = User.objects.get(pk=payload['user_id'])
        if user is None:
            raise exceptions.AuthenticationFailed('User not found')

        return (user, None)


    @staticmethod
    def generate_token(id, scope):
        payload = {
            'user_id': id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=3),
            'iat': datetime.datetime.utcnow(),
            'scope': scope,
        }

        return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')