from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
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

    def validate(self, data):

        # Se valida grupos obligatorio
        if not bool(data["groups"]):
            raise serializers.ValidationError("El rol es requerido.")

        return data

    def create(self, validated_data):
        """
        Sobreescribir el método create para guardar en user
        """
        try:
            with transaction.atomic():
                copy_data = validated_data.copy()
                instance = super().create(validated_data)

                # se guarda la clave
                copy_data["password"] = validated_data['password']
                instance.set_password(copy_data["password"])
                instance.save()

                return instance
        except Exception as error:
            transaction.rollback()
            raise error

    def update(self, instance, validated_data):
        """
        Sobreescribir el método update para guardar en user
        """

        # Se valida en el update  permitir cambiar roles a un usuario si este se encuentra en asignacion de personal
        # unicamente cuando se quiera agregar roles pero no quitar los que tiene
        actual_groups = [
            group.id for group in User.objects.get(id=instance.id).groups.all()
        ]
        new_groups = [group.id for group in validated_data["groups"]]

        actual_groups.sort()
        new_groups.sort()
        new_instance = super().update(instance, validated_data)


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
