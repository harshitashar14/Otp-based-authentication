import base64
import datetime
import traceback

import pyotp
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied, ValidationError
from django.core.mail import send_mail
from django.http import JsonResponse

# Create your views here.
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.exceptions import AuthenticationFailed

from .models import User
from rest_framework_simplejwt.tokens import AccessToken

EXPIRY_TIME = 300


class OtpGenerationView(APIView):
    def post(self, request):
        try:
            print(request.data)
            if not request.data['email']:
                raise ValidationError('email field is required')

            email = request.data['email']
            try:
                user = User.objects.get(email=email)

                if user.is_blocked and user.blocked_at + datetime.timedelta(hours=1) > datetime.datetime.utcnow():
                    raise PermissionDenied("Account is blocked. Please reattempt after some time")
                elif user.is_blocked:
                    user.is_blocked = False
                    user.counter = 0

                if user.otp_created_at and user.otp_created_at > datetime.datetime.utcnow() - datetime.timedelta(
                        minutes=1):
                    raise PermissionDenied("Early consecutive otp request. pLease try after some time")

            except ObjectDoesNotExist as od:
                # create new user
                user = User(email=email)

            key = base64.b32encode(GenerateKey().generate(email).encode())
            otp_obj = pyotp.TOTP(key, interval=EXPIRY_TIME)
            OTP = otp_obj.now()
            user.otp = OTP
            user.otp_created_at = datetime.datetime.utcnow()

            user.save()
            content = f"Otp for email verification is : {OTP}"
            recipient_list = [str(email)]
            send_mail("Email Verification", content, 'Simplifii Verification <' + settings.EMAIL_HOST_USER + '>',
                      recipient_list)
            return JsonResponse({
                'status': 'succeeded',
                'message': 'otp generated successfully',
            }
            )

        except Exception as e:
            traceback.print_exc()
            return JsonResponse({
                'status': 'failed',
                'message': str(e),
            }
            )


class OtpValidationView(APIView):
    def post(self, request):
        try:
            if not request.data['email']:
                raise ValidationError('email field is required')
            if not request.data['otp']:
                raise ValidationError('otp is required')
            email = request.data['email']
            received_otp = request.data['otp']
            try:
                user = User.objects.get(email=request.data['email'])
            except ObjectDoesNotExist as od:
                raise ObjectDoesNotExist('user with this email does not exists')

            if user.is_blocked:
                raise PermissionDenied('Account is blocked. Please re-generate otp after some time')

            key = base64.b32encode(GenerateKey().generate(email).encode())
            otp_obj = pyotp.TOTP(key, interval=EXPIRY_TIME)
            print(otp_obj.now())
            if otp_obj.verify(str(received_otp)):
                user.counter = 0
                user.save()
                return JsonResponse({
                    'status': 'succeeded',
                    'token': str(AccessToken().for_user(user))
                })

            user.counter += 1
            if user.counter == 5:
                user.is_blocked = True
                user.blocked_at = datetime.datetime.utcnow()
            user.save()
            raise ValidationError('OTP is wrong/expired')
        except Exception as e:
            traceback.print_exc()
            return JsonResponse({
                'status': 'failed',
                'message': str(e),
            }, status=404)


class GenerateKey:
    @staticmethod
    def generate(email):
        return str(email) + "" + "simplifill"
