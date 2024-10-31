from django.contrib import admin
from .models import TestModel
from accounts.models import TranscendenceUser

# Register your models here.
admin.site.register(TestModel)
admin.site.register(TranscendenceUser)