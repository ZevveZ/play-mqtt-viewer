from django.shortcuts import render
from django.http import HttpResponse
import json
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from app.models import Users, Sensors, DevicesSensors, Devices, ACLs
from rest_framework import status
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from app.serializers import DeviceSerializer, UserSerializer, SensorsSerializer

# Create your views here.


def test_monitor(request):
    return render(request, 'monitor.html')
    # return render(request, 'img.html')

def test_mcamera(request):
    return render(request, 'mcamera.html')

def test_fr(request):
    return render(request, 'fr.html')

# 从设备推流时忽略跨站伪造请求的检查


@csrf_exempt
def srs_on_publish(request):
    if request.method == 'POST':
        req = json.loads(request.body)
        print(req)
        return HttpResponse(0)
    else:
        return HttpResponse(1)


def srs_on_play(request):
    if request.method == 'POST':
        req = json.loads(request.body)
        print(req)
        return HttpResponse(0)
    else:
        return HttpResponse(1)


@api_view(('GET',))
def api_root(request, format=None):
    return Response({})


@api_view(('POST',))
def users(request, format=None):
    if request.method == 'POST':
        # 注册用户
        req = request.data
        try:
            user = Users(username=req['username'], password=make_password(req['password']), nickname=req['nickname'])
            user.full_clean()
        except Exception as e:
            print('register error')
            return Response('require username, password, nickname', status=status.HTTP_400_BAD_REQUEST)
        user.save()
        return Response(status=status.HTTP_201_CREATED)


@login_required
@api_view(('GET', 'POST', 'DELETE'))
def user(request, username, format=None):
    if request.method=='GET':
        if request.user.username != username:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            serializer = UserSerializer(request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        req = request.data
        user = request.user

        if 'nickname' in req.keys():
            user.nickname = req['nickname']
        if 'password' in req.keys():
            user.password = make_password(req['password'])
        
        device_list = []
        if 'device_list' in req.keys():
            # 删除用户所有的设备, 同时在app_acls表中删除用户对设备的权限
            device_list = req['device_list']
            ACLs.objects.filter(user=user).delete()

        for item in device_list:
            # 判断设备是否存在
            device = Devices.objects.filter(id=item['id'])
            if not device.exists():
                return Response('device id is illegal', status=status.HTTP_400_BAD_REQUEST)
            device = device[0]

            # 判断用户是否拥有此设备, 同时在app_acls表中增加对设备的权限
            if not user.devices.filter(id=device.id).exists():
                ACLs.objects.create(user=user, device=device, clientname=user.username, topic='/'+str(device.id)+'/#', rw=2).save()

        user.save()
        return Response(status=status.HTTP_200_OK)
    elif request.method == 'DELETE':
        request.user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@login_required
@api_view(('POST', 'DELETE'))
def userdevice(request, username, id, format=None):
    user = request.user
    # 判断设备是否存在
    device = Devices.objects.filter(id=id)
    if not device.exists():
        return Response('device id is illegal', status=status.HTTP_400_BAD_REQUEST)
    device = device[0]
    
    if request.method == 'POST':
        # 判断用户是否拥有此设备, 同时在app_acls表中增加对设备的权限
        if not user.devices.filter(id=device.id).exists():
            ACLs.objects.create(user=user, device=device, clientname=user.username, topic='/'+str(device.id)+'/#', rw=2).save()
        return Response(status=status.HTTP_200_OK)
    elif request.method == 'DELETE':
	# 判断用户是否拥有此设备
        if not user.devices.filter(id=device.id).exists():
            return Response('device id is illegal', status=status.HTTP_400_BAD_REQUEST)
        ACLs.objects.get(user=user, device=device).delete()
        return Response(status=status.HTTP_200_OK)


@api_view(('POST', 'DELETE'))
def session(request, format=None):
    if request.method == 'POST':
        # 登陆
        req = request.data;
        try:
            username = req['username']
            password = req['password']
        except KeyError:
            print('login error')
            return Response('require username, password', status=status.HTTP_400_BAD_REQUEST)
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            csrftoken = request.META["CSRF_COOKIE"]
            return Response(csrftoken, status=status.HTTP_200_OK)
        else:
            return Response('username or password error', status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        print('logout')
        # 注销
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)

@login_required
@api_view(('POST', ))
def devices(request, format=None):
    if request.method == 'POST':
        req = request.data
        try:
            newdev = Devices(devicename=req['devicename'], password=make_password(req['password']), nickname=req['nickname'])
            newdev.save()
        except Exception as e:
            return Response('require devicename, password, nickname', status=status.HTTP_400_BAD_REQUEST)
        ACLs.objects.create(device=newdev, clientname=newdev.devicename, topic='/'+str(newdev.id)+'/#', rw=2).save()
        # 更新用户的设备列表
        ACLs.objects.create(user=request.user, device=newdev, clientname=request.user.username, topic='/'+str(newdev.id)+'/#', rw=2).save()
        return Response(status=status.HTTP_201_CREATED)


@login_required
@api_view(('GET', 'POST', 'DELETE'))
def device(request, deviceid, format=None):
    # 判断当前登陆用户是否拥有此设备
    user = request.user
    dev = user.devices.filter(id=deviceid)
    if not dev.exists():
        return Response("this device doesn't belong to you", status=status.HTTP_400_BAD_REQUEST)
    dev = dev[0]
    if request.method == 'GET':
        serializer = DeviceSerializer(dev)
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        req = request.data

        if 'devicename' in req.keys():
            dev.devicename = req['devicename']
            dev.save()
        
        sensor_list = []
        if 'sensor_list' in req.keys():
            sensor_list = req['sensor_list']
        
        for sensor in sensor_list:
            if sensor['sensorcnt'] < 0:
                # 非法数据
                return Response('sensorcnt must greater or equal than 0', status=status.HTTP_400_BAD_REQUEST)
            s = Sensors.objects.filter(sensorname=sensor['sensorname'])
            if not s.exists():
                # 这种类型的传感器不存在
                return Response('no this kind of sensor', status=status.HTTP_400_BAD_REQUEST)
            s = s[0]

            # 判断设备是否已经拥有这种传感器
            ds = dev.devicessensors_set.filter(sensor=s)
            if not ds.exists():
                if sensor['sensorcnt'] > 0:
                    # 为设备添加新的传感器
                    ds = DevicesSensors(device=dev, sensor=s, sensorcnt=sensor['sensorcnt'])
                    ds.save()
            else:
                # 修改设备的传感器数目
                ds = ds[0]
                if sensor['sensorcnt'] > 0:
                    ds.sensorcnt = sensor['sensorcnt']
                    ds.save()
                else:
                    ds.delete()
        return Response(status=status.HTTP_200_OK)
    elif request.method == 'DELETE':
        dev.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@login_required
@api_view(('GET', 'POST',))
def sensors(request, format=None):
    if request.method == 'GET':
        serializer = SensorsSerializer(Sensors.objects.all(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        req = request.data
        try:
            newsensor = Sensors.objects.create(sensorname=req['sensorname'], sensorurl=req['sensorurl'])
            newsensor.save()
        except Exception as e:
            return Response('require sensorname, sensorurl', status=status.HTTP_400_BAD_REQUEST)
        # 注意这里并没有将新添加的传感器添加到设备上
        return Response(status=status.HTTP_201_CREATED)

@login_required
@api_view(('DELETE',))
def sensor(request, sensorname, formate=None):
    if request.method == 'DELETE':
        # 判断sensorname是否存在
        sensors = Sensors.objects.filter(sensorname=sensorname)
        if not sensors.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        sensors.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
