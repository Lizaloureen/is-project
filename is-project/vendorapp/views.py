from clientapp.models import ClientApplication, ClientFirearm, ClientProfile
from rest_framework import viewsets, permissions
from rest_framework.response import Response

from django.db import transaction

from vendorapp.models import Firearm, VendorProfile
from vendorapp.serializers import FirearmSerializer, vendorProfileSerializer

# Create your views here.
   
class VendorProfileView(viewsets.ViewSet):
    serializer_class = vendorProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_profile(self, request):
        user = request.user
        client = VendorProfile.objects.filter(user=user).first()
        if client:
            serializer = self.serializer_class(client, many=False)
            return Response({'data':serializer.data}, status=200)
        else:
            return Response({"error": 'No such client'}, status=500)
        
        
    def update(self, request):
        data = request.data.copy()
        user = request.user
        client = VendorProfile.objects.filter(user=user).first()
        if data.get('company_logo') == "":
            data['company_logo'] = client.company_logo

        if client:
            serializer = self.serializer_class(client, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'data':serializer.data}, status=200)
        else:
            return Response({"error": 'No such client'}, status=500)
        


class FirearmsView(viewsets.ViewSet):
    serializer_class = FirearmSerializer
    permission_classes = [permissions.IsAuthenticated]

    def fa_count(self, request):
        user = request.user
        vendor = VendorProfile.objects.filter(user=user).first()

        firearms = Firearm.objects.filter(vendor=vendor)

        data = {
          "total": firearms.count(),
          'approved': firearms.filter(is_approved = True).count(),
          'issued': firearms.filter(status='Issued').count()
        }
        return Response({'data':data, 'success':True}, status=200)
        

    # List all firearms
    def list(self, request):
        data = request.GET
        user = request.user
        vendor = VendorProfile.objects.filter(user=user).first()

        firearms = Firearm.objects.filter(vendor=vendor).order_by('-create_at')

        if data.get('type'):
            firearms = firearms.filter(firearm_type=data.get('type'))

        serializer = self.serializer_class(firearms, many=True)
        return Response({'data':serializer.data, 'success':True}, status=200)
    

    def create(self, request):
        try:
            data = request.data.copy()
            data['status'] = 'Available'
            data['is_approved'] = True

            user = request.user
            vendor = VendorProfile.objects.filter(user=user).first()
            data['vendor'] = vendor.id

            print('data', data)
            serializer = self.serializer_class(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'message':'Firearm Added', 'success':True}, status=200)
        # else:
            #     return Response({'message':'Invalid Data', 'success':False}, status=400)
        except Exception as e:
            print(e)
            return Response({'message':str(e), 'success':False}, status=400)
        
        
    def update(self, request, id):
        
        data = request.data.copy()
        print('data', data)

        firearm = Firearm.objects.filter(id=id).first()
        if data.get('image') == "":
            data['image'] = firearm.image

        if firearm:
            serializer = self.serializer_class(firearm, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'data':serializer.data}, status=200)
        else:
            return Response({"error": 'No such client'}, status=500)
       

    def issue_firearm(self, request):
        try:
          with transaction.atomic():
            data = request.data.copy()
            firearm_id = data.get('id')
            clientEmail = data.get('clientEmail')
            print('data', data)
            firearm = Firearm.objects.filter(id=firearm_id).first()
            client = ClientProfile.objects.filter(user__email=clientEmail).first()
            if firearm and client:

                if firearm.status == 'Issued':
                    return Response({'message':'Firearm already issued', 'success':False}, status=400)
                
                else:
                    applications = ClientApplication.objects.filter(client=client, status__in=['Approved', 'Confirmed'], type_of_firearm=firearm.firearm_type).first()

                    if not applications:
                        return Response({'message':'Client is not approved to hold firearm', 'success':False}, status=400)
                    else:
                        licenceInstance = applications.client_licence_application.first()
                        fa = ClientFirearm.objects.create(client=client, firearm=firearm, status='Armed', licence=licenceInstance)
                        if fa:
                            firearm.status = 'Issued'
                            firearm.save()
                            return Response({'message':'Firearm Issued', 'success':True}, status=200)
                        else:
                            return Response({'message':'Failed to issue firearm', 'success':False}, status=400)
            else:
                return Response({'message':'Firearm or Client not found', 'success':False}, status=400)  
        except Exception as e:
            print(e)
            return Response({'message':'something went wrong', 'success':False}, status=500)  
    

    def return_firearm(self, request):
        data = request.data
        firearm_id = data.get('id')
        firearm = Firearm.objects.filter(id=firearm_id).first()
        if firearm:
            firearm.status = 'Available'
            firearm.save()

            client_firearm = ClientFirearm.objects.filter(firearm=firearm).first()
            if client_firearm:
                client_firearm.status = 'Disarmed'
                client_firearm.save()

            return Response({'message':'Firearm Returned', 'success':True}, status=200)
        else:
            return Response({'message':'Firearm not found', 'success':False}, status=400)

