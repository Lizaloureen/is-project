from Authapp.models import User
from clientapp.models import ClientApplication, ClientFirearm, ClientLicence, ClientProfile, LicencePayment
from rest_framework import serializers

from vendorapp.models import Firearm



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class ClientProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientProfile
        fields = '__all__'

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        user = User.objects.filter(id=instance.user.id).first()
        rep['user_email'] = user.email
        rep['user_password'] = user.password

        return rep


class ClientApplicationViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientApplication
        fields = '__all__'

    def to_representation(self, instance):
        
        rep = super().to_representation(instance)
        rep['client'] = ClientProfileSerializer(instance.client).data

        return rep


class MiniFirearmSerializer(serializers.ModelSerializer):
    class Meta:
        model = Firearm
        fields = '__all__'

    def to_representation(self, instance):
        from vendorapp.serializers import vendorProfileSerializer
        rep = super().to_representation(instance)
        rep['vendor'] = vendorProfileSerializer(instance.vendor).data

        return rep


class ClientFirearmSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientFirearm
        fields = '__all__'


    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['client'] = ClientProfileSerializer(instance.client).data
        rep['firearm'] = MiniFirearmSerializer(instance.firearm).data
        
        return rep


class ClientLicenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientLicence
        fields = '__all__'

    
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['client'] = ClientProfileSerializer(instance.client).data
        rep['application'] = ClientApplicationViewSerializer(instance.application).data

        client_firearm = ClientFirearm.objects.filter(licence=instance.id).first()
        if client_firearm:
            firearm_data = dict(
                name= client_firearm.firearm.name, 
                id=client_firearm.firearm.id, 
                serial_number=client_firearm.firearm.serial_number, 
                type=client_firearm.firearm.firearm_type, )        
            rep['firearm'] = firearm_data
        else:
            rep['firearm'] = {}

        return rep
    

class LicensePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LicencePayment
        fields = '__all__'
