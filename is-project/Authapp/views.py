from datetime import datetime

from django.core.mail import EmailMessage
from django.shortcuts import render
from django.contrib.auth import login
from django.db import transaction
# from adminApp.threads import SendSmsThread
# from authApp.helpers import generate_otp

from Authapp.serializers import AuthSerializer, RegisterSerializer
from Authapp.models import User, UserOTP
# from adminApp.models.user import AdminProfile
# from fundiApp.models import FundiProfile
from ISPROJECT import settings
from clientapp.models import ClientProfile

from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.authtoken.serializers import AuthTokenSerializer

from knox.views import LoginView as KnoxLoginView

from vendorapp.models import VendorProfile


# Register View 
class RegisterView(viewsets.ViewSet):
    serializer_class = RegisterSerializer

    def create(self, request):
        try:
            with transaction.atomic():
                data = request.data
                print('data', data)
                user_type = data.get("user_type")
                user = None
                data['phone'] = data.get('phone_number')

                serializer = self.serializer_class(data=request.data)
                serializer.is_valid(raise_exception=True)
                user = serializer.save()
                
                if user:
                    print('user', user)

                    if user_type == "Client":
                        user = user
                        first_Name = data.get('first_name')
                        last_Name = data.get('last_name')
                        surname = data.get('surname')
                        ID_Number = data.get('ID_number')
                        phone_number = data.get('phone_number')

                        profile = ClientProfile.objects.create(
                            user=user,
                            first_Name = first_Name,
                            last_Name = last_Name,
                            surname = surname, 
                            ID_Number = ID_Number,
                            phone_number = phone_number
                        )
                        profile.save()

                    if user.user_type == "Vendor":

                        profile = VendorProfile(
                            user=user,
                            name = data.get('name'),
                            company_name = data.get('name'),
                            company_phone = user.phone,
                            company_email = user.email,
                            company_address = data.get('address')
                        )
                        profile.save()

                    # elif user.user_type == "Admin":
                    #     profile = AdminProfile(user=user)
                    #     profile.save()

                    if user:
                        context = {
                            "phone": user.phone,
                            "username": user.email,
                        }


                    mail_from = settings.EMAIL_HOST_USER
                    mail_subject = 'Registration Successful'
                    mail_message = f'\n\n Hello {user.email}, \n\nWelcome on Board.  \nYour registration on Fire licencing Board portal was successful.'
                    mail_to = [user.email]
                    bcc=[mail_from]

                    # Send email
                    email = EmailMessage(mail_subject, mail_message, mail_from, bcc=bcc, to=mail_to)
                    email.send()
                    
                    # otp = generate_otp()
                    # user_otp = UserOTP.objects.create(otp=otp, user=user, is_confirmed=False)
                    # SendSmsThread([user_otp.user.phone], f'Your One Time Password (OTP) is: {user_otp.otp}').start()
                    
                    # send_register_email_task.delay([email, ], "Sycomfy Successful Registration", "email/registration.html", context=context)

                    
                    return Response(
                        {
                            "success": True,
                            "data": serializer.data,
                            "message": "Successfully registered",
                        },
                        status=status.HTTP_201_CREATED,
                    )

        except Exception as e:
            print(e)
            return Response(
                {
                    "success": False,
                    "data": None,
                    "message": "Something went wrong",
                },
                status=500,
            )


    def verify_otp(self, request):
        data = request.data
        otp = data['otp']
        phone = data['phone']
        userOTP = UserOTP.objects.filter(user__phone=phone, otp=otp).first()
        if userOTP:
            rem_min = (datetime.now() - userOTP.updated_at).total_seconds() / 60
            if rem_min >= 30:
                return Response(dict(success=False, message="The OTP has Expired"))
            else:
                userOTP.is_confirmed = True
                userOTP.save()
                return Response(dict(success=True, message="Account verified successfully"))
        else:
            return Response(dict(success=False, message="Account Verification Failed, Invalid OTP"))
    
    def regenerate_otp(self, request):
        data = request.data
        new_otp = generate_otp()
        phone = data['phone']
        userOTP = UserOTP.objects.filter(user__phone=phone).first()
        if userOTP:
            userOTP.otp = new_otp
            userOTP.save()
            SendSmsThread([userOTP.user.phone], f'Your One Time Password (OTP) is: {userOTP.otp}').start()
            return Response(dict(success=True,  otp=new_otp, message="New OTP Regenerated"))
        else:
            return Response(dict(success=False, message="Account Verification Failed"))



# login view 
class LoginView(KnoxLoginView):
    # login view extending KnoxLoginView
    serializer_class = AuthSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        try:
            with transaction.atomic():

                print('request', request.data)
                data = request.data
                serializer = AuthTokenSerializer(data=data)
                serializer.is_valid(raise_exception=True)
                user = serializer.validated_data['user']
                # userOTP = UserOTP.objects.filter(user=user).first()
                # if userOTP and userOTP.is_confirmed == True:
                login(request, user)
                data = super(LoginView, self).post(request, format=None).data
                data['user']['phone'] = user.phone
                data['user']['id'] = user.id

                return Response({'data':data, 'success':True, 'message':'Successfully logged in'}) 
                # else:
                #     return Response({'error':'userotp not confirmed'}) 

        except Exception as e:
            print(e)
            return Response({'success': False, 'message': 'Unable to login user', 'error': str(e)})