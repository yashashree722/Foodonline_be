from django.contrib import admin
from django.urls import path,re_path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework import permissions

from .views import RegisterViews,ProfileView,UserEnableDisableAPI,AdminChangePasswordView,ForgetPasswordAPIView,VerifyResetTokenView,ResetPasswordAPIView,\
CreateRestaurant,PendingRestaurantListAPIView,ApprovePendingRestaurant, \
UpdateRestaurantAPI
urlpatterns=[
    path('register/',RegisterViews.as_view(), name='register'),
    # path('update_profile/', UpdateProfileView.as_view() , name='UpdateProfile'),
    # path('change_password/',ChangePasswordView.as_view()),
    path('update_get_profile/', ProfileView.as_view()),
    path("users/<int:user_id>/status/", UserEnableDisableAPI.as_view()),
    path("change_role/<int:user_id>/", AdminChangePasswordView.as_view(),name='change_role'),
    path("forget_password/" , ForgetPasswordAPIView.as_view()),
    path('verify_token/', VerifyResetTokenView.as_view()),
    path('reset_password/' , ResetPasswordAPIView.as_view()),
    path("restaurant_create/", CreateRestaurant.as_view()),
    path("restaurants_pending/", PendingRestaurantListAPIView.as_view(), name="pending-restaurants"),
    path("restaurants/<int:restaurant_id>/approve_reject/", 
         ApprovePendingRestaurant.as_view(), 
         name="approve-reject-restaurant"),
    path("update_restaurant/",UpdateRestaurantAPI.as_view())

]