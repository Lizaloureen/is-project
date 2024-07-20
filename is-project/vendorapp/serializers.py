from clientapp.models import ClientFirearm
from clientapp.serializer import ClientFirearmSerializer, ClientProfileSerializer
from vendorapp.models import Firearm, VendorProfile
from rest_framework import serializers


class vendorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorProfile
        fields = '__all__'

class FirearmSerializer(serializers.ModelSerializer):
    class Meta:
        model = Firearm
        fields = '__all__'

    def to_representation(self, instance):
        rep = super().to_representation(instance)

        rep['vendor'] = vendorProfileSerializer(instance.vendor).data
        if instance.status == 'Issued':
            client = ClientFirearm.objects.filter(firearm=instance).first()
            if client:
                rep['client'] = ClientFirearmSerializer(client).data

        return rep
        