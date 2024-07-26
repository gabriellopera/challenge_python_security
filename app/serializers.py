from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from app.authentication import generatePassword
from django.db import transaction
from .models import *

class VulnerabilitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vulnerabilities
        fields = [
            'cve_id',
            'name',
            'criticality',
            'status',
            'created_at',
            'last_update_at',
            'description_vulnerabilitie',
            'solution_date',
            'description_solution'
        ]

class VulnerabilitiesPagSerializer(serializers.Serializer):
    
    page_size = serializers.IntegerField(min_value=1, max_value=100, required=True)
    index = serializers.IntegerField(min_value=0, required=True)

    def validate(self, data):
        if "page_size" not in data or "index" not in data:
            raise serializers.ValidationError("Los parámetros index y page_size son obligatorios.")

        return data
    


class GroupSerializer(serializers.ModelSerializer):
    '''
    Serializador de Grupos
    '''

    class Meta:
        '''
        Meta tags
        '''

        model = Group
        fields = (
            'id',
            'name',
            'permissions',
            'user_set'
        )

class UserSerializer(serializers.ModelSerializer):
    """
    User serializer
    """

    groups = GroupSerializer(many=True, read_only=True)
    # user_permissions = PermissionSerializer(many=True, read_only=True)
    class Meta:
        """
        Meta tags
        """

        model = User
        fields = (
            "id",
            "username",
            "email",
            "document",
            "first_name",
            "last_name",
            "is_active",
            "is_superuser",
            "groups"
        )


class SaveUserSerializer(serializers.ModelSerializer):
    """
    User serializer
    """

    # first_name = serializers.CharField(allow_null=True, allow_blank=True)
    # last_name = serializers.CharField(allow_null=True, allow_blank=True)
    # email = serializers.CharField(allow_null=True, allow_blank=True)

    def validate(self, data):

        # Se valida grupos obligatorio
        if not bool(data["groups"]):
            raise serializers.ValidationError("El rol es requerido.")

        return data

    def create(self, validated_data):
        """
        Sobreescribir el método create para guardar en user y user_data
        """
        print('data', validated_data)
        try:
            with transaction.atomic():
                copy_data = validated_data.copy()
                # user_data = validated_data.pop("user_data_user")
                instance = super().create(validated_data)

                # se le asigna clave ramdom (al iniciar session se le asigana la clave de red)
                print("Hola@", instance)
                copy_data["password"] = validated_data['password']
                instance.set_password(copy_data["password"])
                instance.save()

                # # Se crea instancia en user_data
                # user_data["user"] = instance.id
                # serializer_user_data = CreateDataSerializer(data=user_data)
                # serializer_user_data.is_valid(raise_exception=True)
                # serializer_user_data.save()

                return instance
        except Exception as error:
            transaction.rollback()
            raise error

    def update(self, instance, validated_data):
        """
        Sobreescribir el método update para guardar en user y user_data
        """

        # Se valida en el update  permitir cambiar roles a un usuario si este se encuentra en asignacion de personal
        # unicamente cuando se quiera agregar roles pero no quitar los que tiene
        actual_groups = [
            group.id for group in User.objects.get(id=instance.id).groups.all()
        ]
        new_groups = [group.id for group in validated_data["groups"]]

        actual_groups.sort()
        new_groups.sort()
        # user_data_user = validated_data.pop("user_data_user")
        new_instance = super().update(instance, validated_data)
        # # Se actualiza instancia en user_data
        # user_data_user["user"] = instance.id
        # serializer_user_data = CreateDataSerializer(
        #     instance.user_data_user, data=user_data_user
        # )
        # serializer_user_data.is_valid(raise_exception=True)
        # serializer_user_data.save()


        return new_instance
    class Meta:
        """
        Meta tags
        """

        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_active",
            "is_superuser",
            "groups",
            "password"
        )
