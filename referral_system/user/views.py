from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User, Referrals
from .serializers import UserSerializer

from django.contrib.auth.hashers import make_password
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
import random

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
