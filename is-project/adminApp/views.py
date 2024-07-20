from django.shortcuts import render
from django.db import transaction
from rest_framework import viewsets
from rest_framework.response import Response
from django.core.mail import EmailMessage
from adminApp.helpers import create_certificate, generate_random_string, send_sms

from datetime import datetime, timedelta

from ISPROJECT import settings
from vendorapp.models import Firearm, VendorProfile
from vendorapp.serializers import FirearmSerializer, vendorProfileSerializer
from clientapp.models import ClientApplication, ClientFirearm, ClientLicence, ClientProfile, LicencePayment
from clientapp.serializer import ClientApplicationViewSerializer, ClientLicenceSerializer, ClientProfileSerializer


class StatView(viewsets.ViewSet):
    # List all clients
    def list(self, request):
        clients = ClientProfile.objects.all().count()
        applications = ClientApplication.objects.all().count()
        vendors = VendorProfile.objects.all().count()
        firearms = Firearm.objects.all().count()
        return Response({'clients':clients, 'applications':applications, 'vendors':vendors, 'firearms': firearms, 'success':True}, status=200)
    
    def firearms_dist(self, request):
        firearms = Firearm.objects.all().order_by('-create_at')
        data = {}
        for firearm in firearms:
            if firearm.firearm_type in data:
                data[firearm.firearm_type] += 1
            else:
                data[firearm.firearm_type] = 1

        sorted_dict_desc = dict(sorted(data.items(), key=lambda item: item[1], reverse=True))

        return Response({'data':sorted_dict_desc, 'success':True}, status=200)
    
    def app_dist(self, request):
        apps = ClientApplication.objects.all()
        data = {}
        for app in apps:
            if app.region in data:
                data[app.region] += 1
            else:
                data[app.region] = 1
        return Response({'data':data, 'success':True}, status=200)
    

class ClientView(viewsets.ViewSet):
    serializer_class = ClientProfileSerializer

    # List all clients
    def list(self, request):
        clients = ClientProfile.objects.all().order_by('-create_at')
        serializer = self.serializer_class(clients, many=True)
        return Response({'data':serializer.data, 'success':True}, status=200)
    
class ClientsApplicationsView(viewsets.ViewSet):
    serializer_class = ClientApplicationViewSerializer

    # List all clients
    def list(self, request):
        applications = ClientApplication.objects.all().order_by('-id')
        serializer = self.serializer_class(applications, many=True)
        return Response({'data':serializer.data, 'success':True}, status=200)
    
    def approve_interview(self, request):
        data = request.data
        application_id = data.get('id')
        application = ClientApplication.objects.filter(id=application_id).first()
        if application:
            application.interview_date = data.get('interview_date')
            application.status = "Pending_Interview"
            application.save()

            mail_from = settings.EMAIL_HOST_USER
            mail_subject = 'Applications Interview date'
            mail_message = f'Your Interview is scheduled on {data.get("interview_date")}. \nPlease contact the Firearm Licencing board for more information.'
            mail_to = [application.client.user.email, 'olivermulaku@gmail.com']
            bcc=[mail_from]
            
            # Send email
            email = EmailMessage(mail_subject, mail_message, mail_from, bcc=bcc, to=mail_to)
            email.send()
            
            send_sms(application.client.user.phone, f'Your interview has been scheduled for {application.interview_date}')

            return Response({'message':'Interview Date Set', 'success':True}, status=200)
        else:
            return Response({'message':'Application not found', 'success':False}, status=400)
        
    def approve(self, request):

        today = datetime.now().date()
        expiry_date = today + timedelta(days=365)

        data = request.data
        application_id = data.get('id')
        application = ClientApplication.objects.filter(id=application_id).first()
        if application:
            application.status = "Confirmed"
            application.save()
            license_no = generate_random_string(5, 'FAL')

            cl = ClientLicence.objects.filter(license_number=license_no).first()
            if cl:
                license_no = generate_random_string(5, 'FAL')
            else:
                pass

            # save license 
            ClientLicence.objects.create(
                application = application,
                client = application.client,
                license_number = license_no,
                issued_on = today,
                expiry_on = expiry_date,
                status = "Active",
            )
            
            mail_from = settings.EMAIL_HOST_USER
            mail_subject = 'Applications Approved'
            mail_message = f'Find Your Firearm Certificate attached. \nPlease contact the Firearm Licencing board for more information.'
            mail_to = [application.client.user.email, 'olivermulaku@gmail.com']
            bcc=[mail_from]

            # generate pdf certificate
            cert = create_certificate(
                f'{application.client.first_Name} {application.client.last_Name}', 
                "Firearm Licence", 
                today, 
                expiry_date, 
                application.type_of_firearm,
                license_no
                )
            
            # Send email
            email = EmailMessage(mail_subject, mail_message, mail_from, bcc=bcc, to=mail_to)
            email.attach('licence.pdf', cert, 'application/pdf')
            email.send()

            # send sms
            send_sms(application.client.user.phone, f'Your your application was approved. Your certificate has been sent to your email: {application.client.user.email}.')

            return Response({'message':'Application Approved', 'success':True}, status=200)
        else:
            return Response({'message':'Application not found', 'success':False}, status=400)
    
    def reject(self, request):
        data = request.data
        application_id = data.get('id')
        application = ClientApplication.objects.filter(id=application_id).first()
        if application:
            application.status = "Rejected"
            application.save()
            
            mail_from = settings.EMAIL_HOST_USER
            mail_subject = 'Applications Rejected'
            mail_message = f'Your Firearm Application has been rejected. \nPlease contact the Firearm Licencing board for more information.'
            mail_to = []
            bcc=[mail_from]
            EmailMessage(mail_subject, mail_message, mail_from, bcc=bcc, to=mail_to).send()
        
            return Response({'message':'Application Rejected', 'success':True}, status=200)
        else:
            return Response({'message':'Application not found', 'success':False}, status=400)
    

class LicenceView(viewsets.ViewSet):
    serializer_class = ClientLicenceSerializer

    # List all vendors
    def list(self, request):
        # Active
        # Awaiting Payment Approval
        # Awaiting Interview
        # Expired', 'Expired
        # Revoked
        data = request.GET
        status = data.get('status')
        licenses = ClientLicence.objects.all().order_by('-create_at')

        if status:
            licenses = licenses.filter(status=status).order_by('-create_at')

        serializer = self.serializer_class(licenses, many=True)
        return Response({'data':serializer.data, 'success':True}, status=200)
    

    def confirm_payment(self, request):
        try:
            with transaction.atomic():
                data = request.data.copy()
                trans_id = data.get('trans_id')
                license_id = data.get('licence_id')
                interview_date = data.get('interview_date')
                license = ClientLicence.objects.filter(id=license_id).first()
                if license:
                    payment = LicencePayment.objects.filter(transaction_id=trans_id).first()
                    if payment:
                        payment.confirmed = True
                        payment.confirmed_on = datetime.now().date()
                        payment.save()
                    else:
                        return Response({'message':'Payment not found', 'success':False}, status=400)
                    
                    license.status = 'Awaiting Interview'
                    license.interview_on = interview_date
                    license.save()

                    mail_from = settings.EMAIL_HOST_USER
                    mail_subject = 'Licence Renew Payment Confirmation'
                    mail_message = f'Your Payment on Firearm licence serial no: {license.license_number} has been confirmed. Interview is scheduled on date: {interview_date} \n\nPlease contact the Firearm Licencing board for more information.'
                    mail_to = [license.client.user.email]
                    bcc=[mail_from]
                    EmailMessage(mail_subject, mail_message, mail_from, bcc=bcc, to=mail_to).send()

                    return Response({'message': 'payment confirmed','success':True}, status=200)
                else:
                    return Response({'message':'Licence not found', 'success':False}, status=400)
        except Exception as e:
            print('eeee',e)
            return Response({'message':str(e), 'success':False}, status=400)


    def change_status(self, request):
        today = datetime.now().date()
        data = request.data.copy()
        status = data.get('status') 
        license_id = data.get('id')
        license = ClientLicence.objects.filter(id=license_id).first()
        if license:
            # Active
            # Awaiting Payment Approval
            # Awaiting Interview
            # Expired', 'Expired
            # Revoked

            if status == 'Active':
                license.status = status
                license.renewed_on = today
                license.expiry_on = today + timedelta(days=365)
                license.save()

                mail_from = settings.EMAIL_HOST_USER
                mail_subject = 'Licence Renewed'
                mail_message = f'Your Firearm licence serial no: {license.license_number} has been renewed. \nPlease contact the Firearm Licencing board for more information.'
                mail_to = []
                bcc=[mail_from]
                EmailMessage(mail_subject, mail_message, mail_from, bcc=bcc, to=mail_to).send()
                serializer = self.serializer_class(license, many=False)
                return Response({'data':serializer.data, 'success':True}, status=200)

            if status == 'Revoked':
                license.status = status
                license.revoked_on = today
                license.save()

                mail_from = settings.EMAIL_HOST_USER
                mail_subject = 'Licence Revoked'
                mail_message = f'Your Firearm licence serial no: {license.license_number} has been revoked. You are adviced to surrender you firearm 7 day from the date of revocation \nPlease contact the Firearm Licencing board for more information.'
                mail_to = []
                bcc=[mail_from]
                EmailMessage(mail_subject, mail_message, mail_from, bcc=bcc, to=mail_to).send()
                serializer = self.serializer_class(license, many=False)
                return Response({'data':serializer.data, 'success':True}, status=200)

            if status == 'Expired':
                license.status = status
                license.revoked_on = today
                license.save()

                mail_from = settings.EMAIL_HOST_USER
                mail_subject = 'Licence Has Expired'
                mail_message = f'Your Firearm licence serial no: {license.license_number} has expired. You are adviced to renew it immediately \nPlease contact the Firearm Licencing board for more information.'
                mail_to = []
                bcc=[mail_from]
                EmailMessage(mail_subject, mail_message, mail_from, bcc=bcc, to=mail_to).send()
                serializer = self.serializer_class(license, many=False)
                return Response({'data':serializer.data, 'success':True}, status=200)


    

class VendorsView(viewsets.ViewSet):
    serializer_class = vendorProfileSerializer

    # List all vendors
    def list(self, request):
        vendors = VendorProfile.objects.all().order_by('-create_at')
        serializer = self.serializer_class(vendors, many=True)
        return Response({'data':serializer.data, 'success':True}, status=200)
    
    
class FirearmsView(viewsets.ViewSet):
    serializer_class = FirearmSerializer

    # List all firearms
    def list(self, request):
        data = request.GET

        firearms = Firearm.objects.all().order_by('-create_at')
        if data.get('vendor'):
            firearms = firearms.filter(vendor__id=int(data.get('vendor')))

        if data.get('type'):
            firearms = firearms.filter(firearm_type=data.get('type'))
        
        for firearm in firearms:
            if firearm.status == 'Issued':
                client = ClientFirearm.objects.filter(firearm=firearm).first()
                if client:
                    firearm.client = client
                    # rep['client'] = ClientFirearmSerializer(client).data


        serializer = self.serializer_class(firearms, many=True)
        return Response({'data':serializer.data, 'success':True}, status=200)
    

    def create(self, request):
        try:
            data = request.data.copy()
            data['status'] = 'Available'
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
    


    def approve(self, request):
        data = request.data
        firearm_id = data.get('id')
        firearm = Firearm.objects.filter(id=firearm_id).first()
        if firearm:
            firearm.is_approved = True
            firearm.save()
            return Response({'message':'Approved firearm', 'success':True}, status=200)
        else:
            return Response({'message':'Firearm not found', 'success':False}, status=400)  



    def change_status(self, request):
        data = request.data
        firearm_id = data.get('id')
        status = data.get('status')
        firearm = Firearm.objects.filter(id=firearm_id).first()
        if firearm:
            firearm.status = status
            firearm.save()
            return Response({'message':'Status Changed', 'success':True}, status=200)
        else:
            return Response({'message':'Firearm not found', 'success':False}, status=400)  


    def issue_firearm(self, request):
        data = request.data
        firearm_id = data.get('id')
        client_id = data.get('client_id')
        firearm = Firearm.objects.filter(id=firearm_id).first()
        client = ClientProfile.objects.filter(id=client_id).first()
        if firearm and client:
            if firearm.status == 'Issued':
                return Response({'message':'Firearm already issued', 'success':False}, status=400)
            
            applications = ClientApplication.objects.filter(client=client, status='Approved', type_of_firearm=firearm.firearm_type).first()

            if not applications:
                return Response({'message':'Client is not approved to hold firearm', 'success':False}, status=400)
            else:
                license = ClientLicence.objects.filter(status='Active', client=client, application=applications).first()
                if license:
                    if ClientFirearm.objects.filter(licence=license, status='Armed').first():
                        return Response({'message':'Client has already licenced another firearm with this licence', 'success':False}, status=400)
                    
                    firearm.status = 'Issued'
                    firearm.save()

                    ClientFirearm.objects.create(client=client, firearm=firearm, status='Armed', licence=license)

                    return Response({'message':'Firearm Issued', 'success':True}, status=200)
                else:
                    return Response({'message':'Client has no active Licence to own this firearm', 'success':False}, status=400)
        else:
            return Response({'message':'Firearm or Client not found', 'success':False}, status=400)  
    

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


