from django.contrib.auth.models import User
from django.shortcuts import render

# Create your views here.
# reject brokers with active = False
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
