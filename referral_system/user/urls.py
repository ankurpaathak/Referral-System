from django.urls import path
from .views import UserRegistration, UserLogin, UserLogout, UserDetails, UserReferrals

urlpatterns = [
    path('register/', UserRegistration.as_view(), name='register'),
    path('login/', UserLogin.as_view(), name='login'),
    path('logout/', UserLogout.as_view(), name='logout'),
    path('get/', UserDetails.as_view(), name='UserDetails'),
    path('referrals/', UserReferrals.as_view(), name='UserReferrals'),
]