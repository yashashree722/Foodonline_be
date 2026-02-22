from django.shortcuts import render
from rest_framework.views import APIView

from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.viewsets import ModelViewSet
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from .serializers import RegisterSerializer, ProfileSerailizer,ChangepasswordSerializer,UserEnableDisableSeralizer ,ChangeUserRoleSerializer ,ResetPasswordSerializer,VerifyTokenSerializer,ForgetPasswordserializer ,\
RestaurantSeralizer,PendingRestaurantSerializer, ApprovePendingSerializer, RestaurantUpdateSerializer
from .permissions import IsAdminUser,IsRestaurantOwner
from rest_framework import status
from .models import User,Profile, Restaurant
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

# Create your views here.

class RegisterViews(APIView):
    permission_classes=[AllowAny]
    authentication_classes =[]
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"Message" :"User Register", "user": serializer.data}, status=201)
    

# from .serializers import ProfileSeralizer
# class UpdateProfileView(APIView):
#     # aut = [IsAuthenticated]
#     authentication_classes=[IsAuthenticated]
#     permission_classes=[]
#     def get(self, request):
#         profile = request.user.profile
#         serializer = ProfileSerailizer(profile)
#         return Response(serializer.data)

#     def patch(self, request):
#         profile = request.user.profile
#         serializer = ProfileSeralizer(
#             instance=profile,
#             data=request.data,
#             partial=True,
#         )
#         serializer.is_valid(raise_exception=True)
#         serializer.save()

#         return Response({
#             "message": "Updated successfully",
#             "user": serializer.data
#         })

    

class AdminChangePasswordView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self, request):
        serializer = ChangepasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response({"message" : "Old password is incorrect"})
        
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({"message" : "password set successfully"})
    

from rest_framework.permissions import IsAuthenticated

class ProfileView(APIView):
    permission_classes=[IsAuthenticated]
    
    def get(self,request):
        profile = request.user.profile
        serialiozer = ProfileSerailizer(profile)
        return Response(serialiozer.data)
    
    def patch(self, request, *args, **kwargs):
        instance = request.user.profile
        profile = request.data
        serializer = ProfileSerailizer(instance , data=profile,partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response (serializer.data)



class UserEnableDisableAPI(APIView):
    permission_classes =[IsAuthenticated,IsAdminUser]
    def patch(self, request, user_id):
        user = get_object_or_404(User,id=user_id)
        serializer = UserEnableDisableSeralizer(user, data = request.data, partial =True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        status = "activated" if serializer.data['is_active'] else "deactivated"


        return Response({
            "message": f"user{status} succesfuly",
            "user_id" : user.id,
            "is_active" : serializer.data['is_active']
        })


class ChangeUserRole(APIView):
    permission_classes =[IsAuthenticated, IsAdminUser]
    def patch(self, request ,user_id):
        user = get_object_or_404(User, id = user_id)
        serializer = ChangeUserRoleSerializer(user ,  data = request.data, partial = True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            "data" :serializer.data
        })

    


class ForgetPasswordAPIView(APIView):
    def post (self, request):
        serializer = ForgetPasswordserializer(data= request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        try :
            user = User.objects.get(email= email)
        except User.DoesNotExist:
            return Response(
                {
                "message": "If email exists, reset link sent"},
                status=status.HTTP_200_OK
                )
        
        if user.role=='ADMIN':
            return Response({"error" : "admin can not change password"}, status=403)
        
        token_obj = PasswordResetToken.objects.create(user=user,expires_at = timezone.now() +timedelta(minutes=15))
        reset_link = f"http://localhost:8000/reset-password?token={token_obj.token}"
        send_mail(
            subject="Password Reset",
            message=f"Click link to reset password: {reset_link}",
            from_email="pradipbankar0097@gmail.com",
            recipient_list=[email],
        )

        return Response({"message": "Password reset link sent",
                         "token" :str(token_obj.token)
                         }, status=200)



class VerifyResetTokenView(APIView):
    def get(self, request):
            token = request.query_params.get("token")

            if not token:
                return Response({"error": "Token missing"}, status=400)

            reset_token = get_object_or_404(PasswordResetToken, token=token)

            if reset_token.is_used:
                return Response({"error": "Token already used"}, status=400)

            if reset_token.expires_at < timezone.now():
                return Response({"error": "Token expired"}, status=400)

            return Response({"message": "token is valid"})




class ResetPasswordAPIView(APIView):
    def put(self, request):
        serializer = ResetPasswordSerializer(data= request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']
        reset_token = get_object_or_404(PasswordResetToken, token= token)
        if reset_token.is_used:
            return Response({
                "message": "Token already used"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if reset_token.expires_at < timezone.now():
            return  Response({
                "message" :"Already expired"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user = reset_token.user

        user.set_password(new_password)
        user.save()
        reset_token.is_used= True
        reset_token.save()
        return Response({
            "message": "Password reset succesfully"
        }, status=status.HTTP_200_OK)


class CreateRestaurant(APIView):
    permission_classes= [IsRestaurantOwner]
    def post(self, request):
        serializer = RestaurantSeralizer(data= request.data)
        serializer.is_valid(raise_exception=True)
        reataurant =serializer.save(owner =request.user)
        return Response({
            "message" :"restaurant created and waiting for admin approval",
            # "data": serializer.data,
            "details" : RestaurantSeralizer(reataurant).data
        })

class PendingRestaurantListAPIView(APIView):
    permission_classes =[IsAdminUser]
    def get(self,request):
        res = Restaurant.objects.filter(is_active=False)
        serializer = PendingRestaurantSerializer(res,many=True)
        return Response({
            "Response" : serializer.data
        })
    

class ApprovePendingRestaurant(APIView):
    permission_classes =[IsAdminUser]
    def patch(self , request , restaurant_id):
        res = get_object_or_404(Restaurant, id =restaurant_id, status='PENDING')
        serializer = ApprovePendingSerializer(res,data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        print("'''''''''''''''''",serializer.validated_data)
        status_value = serializer.validated_data['status']
        if status_value == "APPROVED":
            res.is_active = True
            res.status='APPROVED'
        elif status_value == "REJECTED":
            res.is_active = False
            res.status='REJECTED'
        serializer.save()
        return Response({
            "message": f"Restaurant {status_value.lower()} successfully",
            "restaurant_id": res.id,
            "status": res.status
        })


class UpdateRestaurantAPI(APIView):
    permission_classes =[IsRestaurantOwner]
    def patch(self, request):
        restauant = get_object_or_404(Restaurant,owner= request.user)
        if not restauant:
            return Response({
                "data" :"Not valid id"
            }, status= status.HTTP_400_BAD_REQUEST)
        if restauant.status != 'APPROVED':
            return Response({
                "data" :"Restauant not approved  yet"
            },status= status.HTTP_400_BAD_REQUEST)
        serializer = RestaurantUpdateSerializer(restauant, data= request.data, partial= True)
        serializer.is_valid()
        
        
        serializer.save()
        return Response({
            "message" :"Updated Restauant"
        }, status= status.HTTP_201_CREATED)

        
            
        