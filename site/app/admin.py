from django.contrib import admin
from app.models import Sensors, Devices, Users, DevicesSensors
from django.forms import ModelForm, PasswordInput, CharField
# Register your models here.

class UsersForm(ModelForm):
    password = CharField(widget=PasswordInput)
    class Meta:
        model = Users
        fields = '__all__'


class UsersAdmin(admin.ModelAdmin):
    form = UsersForm


class DevicesForm(ModelForm):
    class Meta:
        model = Devices
        fields = '__all__'
        widgets = {
            'password' : PasswordInput()
        }


class DevicesAdmin(admin.ModelAdmin):
    form = DevicesForm


admin.site.register(Sensors)
admin.site.register(Devices, DevicesAdmin)
admin.site.register(Users, UsersAdmin)
admin.site.register(DevicesSensors)