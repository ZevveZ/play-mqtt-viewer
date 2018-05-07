from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class Sensors(models.Model):
    sensorname = models.CharField(max_length=150, unique=True)
    sensorurl = models.CharField(max_length=150)

class Devices(models.Model):
    devicename = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)
    nickname = models.CharField(max_length=30)
    sensors = models.ManyToManyField(Sensors, through='DevicesSensors', through_fields=('device', 'sensor'))

class DevicesSensors(models.Model):
    device = models.ForeignKey(Devices, on_delete=models.CASCADE)
    sensor = models.ForeignKey(Sensors, on_delete=models.CASCADE)
    sensorcnt = models.IntegerField(default=0)

class Users(AbstractUser):
    nickname = models.CharField(max_length=50, blank=True)
    devices = models.ManyToManyField(Devices, through='ACLs')
    class Meta(AbstractUser.Meta):
        pass


# 这个模型记录了用户与设备之间的关系, 还作为MQTT服务器的访问控制列表
class ACLs(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, blank=True, null=True)
    device = models.ForeignKey(Devices, on_delete=models.CASCADE)
    clientname = models.CharField(max_length=150)
    topic = models.CharField(max_length=256)
    rw = models.IntegerField(default=0)