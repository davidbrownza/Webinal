from rest_framework import serializers
from django.contrib.auth.models import User
from filemanager.models import *

class TabListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tab