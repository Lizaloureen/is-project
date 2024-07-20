from django.shortcuts import render
from django.db import transaction
from Authapp.models import User
from adminApp.helpers import send_sms
from clientapp.helpers import send_mail
from clientapp.models import ClientApplication, ClientFirearm, ClientLicence, ClientProfile, LicencePayment
from rest_framework import viewsets, permissions
from rest_framework.response import Response

from clientapp.serializer import ClientApplicationViewSerializer, ClientFirearmSerializer, ClientLicenceSerializer, ClientProfileSerializer,  LicensePaymentSerializer
# from vendorapp.models import Firearm

class StatsView(viewsets.ViewSet):
    
    def stats(self, request):
        user = request.user
        client= ClientProfile.objects.filter(user=user).first()
        application = ClientApplication.objects.filter(client=client).count()
        firearms = ClientFirearm.objects.filter(client=client).count()
        licences= ClientLicence.objects.filter(client=client)
        renewal= licences.filter(status='Expired').count()
        licence=licences.count()

        data= dict(application=application, firearms=firearms, renewal=renewal, licence=licence)

        return Response({'data':data}, status=200)


class ClientProfileView(viewsets.ViewSet):
    serializer_class = ClientProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_profile(self, request):
        user = request.user
        client = ClientProfile.objects.filter(user=user).first()
        if client:
            serializer = self.serializer_class(client, many=False)
            return Response({'data':serializer.data}, status=200)
        else:
            return Response({"error": 'No such client'}, status=500)
        
        
    def update(self, request):
        data = request.data
        user = request.user
        client = ClientProfile.objects.filter(user=user).first()
        if client:
            serializer = self.serializer_class(client, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'data':serializer.data}, status=200)
        else:
            return Response({"error": 'No such client'}, status=500)


# Client applications
class ClientApplicationView(viewsets.ViewSet):
    serializer_class = ClientApplicationViewSerializer
    permission_classes = [permissions.IsAuthenticated]

    # get client applications 
    def get_applications(self, request):
        try:
            user = request.user        
            client = ClientProfile.objects.filter(user=user).first()
            clientApplications = ClientApplication.objects.filter(client=client).order_by('-create_at')
            # mail_to = [user.email]
            # send_mail(mail_subject='Applications', mail_message='Applications list triggered.', mail_to=mail_to)
            if clientApplications:
                serializer = self.serializer_class(clientApplications, many=True)
                return Response({'message': 'success', "data":serializer.data}, status=200)                
            else:
                return Response({'message':"No Applications found"}, status=400)  
        except Exception as e:
            return Response({"error": str(e)}, status=500)
        
    # get client applications stats
    def get_application_stats(self, request):
        try:
            user = request.user        
            client = ClientProfile.objects.filter(user=user).first()
            clientApplications = ClientApplication.objects.filter(client=client).order_by('-create_at')
            if clientApplications:
                con = clientApplications.filter(status='Confirmed').count()
                appr = clientApplications.filter(status='Approved').count()

                data = {
                    'total': clientApplications.count(),
                    'pending': clientApplications.filter(status='Pending').count(),
                    'approved': con + appr,
                    'rejected': clientApplications.filter(status='Rejected').count(),
                    'pending_interview': clientApplications.filter(status='Pending_Interview').count(),
                }
                return Response({'message': 'success', "data":data}, status=200)                
            else:
                return Response({'message':"No Applications found"}, status=400)  
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    # client application 
    def create(self, request):
        try:
            with transaction.atomic():                
                user = request.user    
                print('user', user, User.objects.count())   

                client = ClientProfile.objects.filter(user=user).first()
                if client:
                    data = request.data.copy()
                    print('data', data)
                    data['client'] = client.id
                    serializer = self.serializer_class(data=data)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    return Response({'message': 'success', 'success': True, 'data':serializer.data}, status=201)
                else:
                    return Response({'message':"No such client"}, status=400)
            
        except Exception as e:
            return Response({"error": str(e), 'success': False}, status=500)


class ClientLicenceView(viewsets.ViewSet):
    serializer_class = ClientLicenceSerializer
    license_payment_serializer = LicensePaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        try:
            user = request.user      
            client = ClientProfile.objects.filter(user=user).first()

            licenses = ClientLicence.objects.filter(client=client).order_by('-create_at')
            if licenses:
                serializer = self.serializer_class(licenses, many=True)
                return Response({'message': 'success', "data":serializer.data}, status=200)                
            else:
                return Response({'message':"No Licences found"}, status=200)  
        except Exception as e:
            return Response({"error": str(e)}, status=500)
        

    def renew(self, request):
        try:
            with transaction.atomic():
                data = request.data.copy()
                license_id = data.get('id')
                data['licence'] = license_id
                transaction_id = data.get('trans_id')
                licence = ClientLicence.objects.filter(id=license_id).first()
                if licence:

                    trans = LicencePayment.objects.filter(transaction_id=transaction_id).first()
                    if not trans:
                        new_trans = LicencePayment.objects.create(transaction_id = transaction_id,licence = licence)
                        
                        licence.status = 'Awaiting Payment Approval'
                        licence.save()

                        serializer = self.license_payment_serializer(new_trans)
                        # serializer.is_valid(raise_exception=True)
                        # serializer.save()
                         # send sms
                        send_sms(request.user.phone, f'Your payment was received. Once approved you willl be notified via you mail: {request.user.email}.')

                        return Response({'message': 'Payment was Successful... You will be notified on email once payment is confirmed', 'success': True, 'data':serializer.data}, status=201)
             
                    else:
                        return Response({'message': 'The transaction id is incorrect', 'status':False}, status=400)  
                   

                    # send sms
                    send_sms(request.user.phone, f'Your payment was received. Once approved you willl be notified via you mail: {request.user.email}.')

                    return Response({'message': 'Payment was Successful... You will be notified on email once payment is confirmed', 'success': True, 'data':serializer.data}, status=201)
                else:
                    return Response({'message':"No such licence"}, status=400)

        
        except Exception as e:
            return Response({"error": str(e)}, status=500)



# Client firearms
class ClientFirearmsView(viewsets.ViewSet):
    serializer_class = ClientFirearmSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_client_firearms(self, request):        
        try:
            user = request.user   
            client = ClientProfile.objects.filter(user=user).first()     
            firearms = ClientFirearm.objects.filter(client=client).order_by('-create_at')
            firearms_stat = firearms.filter(status='Armed').count()
            fa_data = {
                'total': firearms_stat
            }
           
            serializer = self.serializer_class(firearms, many=True)
            return Response({'message': 'success', "data": serializer.data, 'fa_data': fa_data}, status=200)                
            
        except Exception as e:
            print('eee', e)
            return Response({"error": str(e)}, status=500)

    def firearm_stats(self, request):        
        try:
            user = request.user  
            client = ClientProfile.objects.filter(user=user).first()     
            firearms = ClientFirearm.objects.filter(client=client, status='Armed').count()
            data = {
                'total': firearms
            }
           
            return Response({'message': 'success', "data": data}, status=200)                
            
        except Exception as e:
            print('eee', e)
            return Response({"error": str(e)}, status=500)

    def details(self, request):
        try:
            user = request.user        
            client = ClientProfile.objects.filter(user=user).first()
            firearms = ClientFirearm.objects.filter(client=client).order_by('-create_at')
            if firearms:
                serializer = self.serializer_class(ClientFirearm, many=True)
                return Response({'message': 'succes', "data":serializer.data}, status=200)                
            else:
                return Response({'message':"No Firearms found"}, status=200) 
            
        except Exception as e:
            return Response({"error": str(e)}, status=500)
        
