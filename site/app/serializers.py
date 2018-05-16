from rest_framework import serializers
from app.models import Users, Devices, Sensors, DevicesSensors

class DevicesSensorsSerializer(serializers.ModelSerializer):
    sensorname = serializers.ReadOnlyField(source='sensor.sensorname')  # source里面的是sensor不是模型名sensors
    sensorurl = serializers.ReadOnlyField(source='sensor.sensorurl')
    class Meta:
        model = DevicesSensors
        fields = ('sensorname', 'sensorurl', 'sensorcnt')

# class SensorListSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Sensors
#         fields = ('sensorname','sensorurl')

class DeviceSerializer(serializers.ModelSerializer):
    sensor_list = DevicesSensorsSerializer(source='devicessensors_set', many=True, read_only=True)

    class Meta:
        model = Devices
        fields = ('devicename','nickname', 'sensor_list')

class DeviceListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Devices
        fields = ('id', 'devicename')


class UserSerializer(serializers.ModelSerializer):
    device_list = DeviceListSerializer(source='devices', read_only=True, many=True)
    
    class Meta:
        model = Users
        fields = ('nickname', 'device_list')

class SensorsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sensors
        fields = ('sensorname', 'sensorurl')
