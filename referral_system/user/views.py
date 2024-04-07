from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User, Referrals
from .serializers import UserSerializer, LoginSerializer

from django.contrib.auth.hashers import make_password
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
import random
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django.contrib.auth import logout
from datetime import timedelta
from django.utils import timezone
from rest_framework.pagination import PageNumberPagination



class GetUserIdFromToken:

    def get_user_id(self, request):
        try:
            token_header = request.headers.get('Authorization')
            token = str.split(token_header, ' ')[1]
            token_obj = Token.objects.get(key=token)
            user_id = token_obj.user_id
            return user_id
        except Token.DoesNotExist:
            return None
        

def generate_refer_code(name):
    cleaned_user_name = name.replace(" ", "").upper()
    name_part = cleaned_user_name[:3]
    
    while True:
        random_number = str(random.randint(10000, 99999))
        refer_code = name_part + random_number
        refer_code_object = User.objects.filter(refer_code=refer_code).first()
        if not refer_code_object:
            return refer_code


@permission_classes((AllowAny,))
class UserRegistration(APIView):

    def post(self, request):

        referral_code = request.data.get('referral_code')
        name = request.data.get('name')
        if len(name) < 3:
            return Response({"message": "Name should be minimum 3 character"})
        
        refer_code = generate_refer_code(name)
        password = make_password(request.data.get('password'))
        request.data['password'] = password
        request.data['refer_code'] = refer_code
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            if referral_code:
                refer_by = User.objects.filter(refer_code=referral_code).first()
                if refer_by:
                    referral = User.objects.filter(email=request.data.get('email')).first()
                    refer_by.referral_points += 10
                    refer_by.save(update_fields=['referral_points', 'updated_at'])
                    Referrals.objects.create(refer_by=refer_by, referral=referral).save()
            return Response({"user_id": user.id, "message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetails(APIView):
    user = GetUserIdFromToken()

    def get(self, request):
        user_id = self.user.get_user_id(request)
        if user_id is not None:
            user_object = User.objects.filter(id=user_id).first()
            if user_object:
                serializer = UserSerializer(user_object)
                user_dict = {
                    'name': serializer.data['name'],
                    'email': serializer.data['email'],
                    'referral_code': serializer.data['refer_code'],
                    'created_at': serializer.data['created_at']
                }
                return Response(user_dict)
            return Response(user_object)
        return Response()


class UserReferrals(APIView):
    user = GetUserIdFromToken()
    pagination_class = PageNumberPagination
    pagination_class.page_size = 20

    def get(self, request):

        user_id = self.user.get_user_id(request)
        if user_id is not None:
            user_object = User.objects.filter(id=user_id).first()
            if user_object:
                referrals_user = Referrals.objects.filter(refer_by=user_id).select_related('referral')
                paginator = self.pagination_class()
                result_page = paginator.paginate_queryset(referrals_user, request)
                user_list = []
                for user in result_page:
                    serializer = UserSerializer(user.referral)
                    user_list.append({
                        'name': serializer.data['name'],
                        'email': serializer.data['email'],
                        'referral_code': serializer.data['refer_code'],
                        'created_at': serializer.data['created_at']
                    })
                return paginator.get_paginated_response(user_list)
            return Response(user_object)
        return Response()


class UserLogin(ObtainAuthToken):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        token.expires = timezone.now() + timedelta(days=7)
        token.save()
        return Response({'token': token.key, 'created_at': token.created})


class UserLogout(APIView):
    def post(self, request):
        try:
            token = request.META['HTTP_AUTHORIZATION'].split('token ')[1]
            Token.objects.get(key=token).delete()
            logout(request)
            return Response({"message": "User logged out successfully."}, status=status.HTTP_200_OK)
        except (KeyError, Token.DoesNotExist):
            return Response({"message": "Invalid token or user not authenticated."},
                            status=status.HTTP_401_UNAUTHORIZED)