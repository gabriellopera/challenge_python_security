from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from random import choice
from rest_framework_jwt import utils

class CustomBackend(ModelBackend):
    """
    Documentación oficial
    https://docs.djangoproject.com/en/1.11/topics/auth/customizing/#specifying-authentication-backends

    Leer los siguientes títulos para entender el proceso
        - Specifying authentication backends
        - Writing an authentication backend
    """

    def authenticate(self, request, username=None, password=None):
        """
        request: objecto de la petición actual
        username: username que se envió por la petición
        password: password que se envió por la petición
        """
        try:
            # Consultar el usuario en la aplicación solo por username
            user_exist_django = User.objects.get(username=username)

            # Chequear que el password coincida con el de aplicación
            if not user_exist_django.check_password(password):
                raise ValidationError('Invalid password')

        except User.DoesNotExist:
            # None cuando NO existe el usuario en aplicación
            user_exist_django = None
        except ObjectDoesNotExist:
            # None cuando no encuentra información en user_data
            user_exist_django = None

        return user_exist_django


def jwt_response_payload_handler(token, user=None, request=None):
    """
    Personalizar los datos que se devolveran después de que un usuario se autentique
    por medio del jwt

    Se ejecuta después de que jwt autentique el usuario. Se configura en el settings,
    en el diccionario JWT_AUTH con clave JWT_RESPONSE_PAYLOAD_HANDLER

    Leer el siguiente link para entender el proceso
    https://getblimp.github.io/django-rest-framework-jwt/#additional-settings

    token:      token generado cuando el usuario se autentico
    user:       instancia del usuario autenticado
    request:    objeto de la petición actual
    """
    # Info del usuario a retornar
    user_info = {
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "is_superuser": user.is_superuser,
        "id": user.id,
    }

    # Crear lista de permisos y consultar todos los grupos asociados al usuario
    permissions = []
    groups_list = []
    groups = user.groups.all()
    user_permissions = user.user_permissions.all()

    # Recorrer los grupos
    for group in groups:
        # print('grupo', group.name)
        groups_list.append({"id": group.id, "group": group.name})
        # Recorrer todos los permisos de cada grupo y asignarlos
        for permission in group.permissions.all():
            permissions.append(permission.codename)

    # Recorrer los permisos directos al usuario
    for permission in user_permissions:
        if permission not in permissions:
            permissions.append(permission.codename)

    # Retornar el token y la info que deseas (Esta debe ser serializable)
    return {
        "token": token,
        "user": user_info,
        "permissions": permissions,
        "groups": groups_list,
    }


def jwt_payload_handler(user):
    payload = utils.jwt_payload_handler(user)

    return payload



def generatePassword(self):
  '''
  Método que genera contraseña aleatorias
  '''
  longitud = 10
  valores = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ<=>@#%&+"

  valueRandom = ""
  valueRandom = valueRandom.join([choice(valores) for i in range(longitud)])
  return valueRandom