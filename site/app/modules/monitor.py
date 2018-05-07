import paho.mqtt.client as mqtt
import re
import json
from decimal import Decimal
import ssl

# LepDClient
def split_to_lines(longString):
    return re.split(r'\\n|\n', longString.strip())

def toDecimal(val, precision='0.00'):
    try:
        return float(val) #Decimal(val).quantize(Decimal(precision))
    except Exception as err:
        print(err)
        return float(0)


def cpu_stat(response_lines):
    if(len(response_lines) < 3):
        return {}
    try:
        # discard the first three lines
        response_lines.pop(0)
        response_lines.pop(0)
        response_lines.pop(0)
    except Exception as e:
        print(response_lines, "-------  GetCmdMpstat")
        return {}

    irq_data = {}
    irq_data['data'] = {}

    for line in response_lines:

        if (line.strip() == ''):
            break

        line_values = line.split()

        irq_stat = {}
        try:
            irq_stat['idle'] = float(line_values[-1])
            irq_stat['gnice'] = float(line_values[-2])
            irq_stat['guest'] = float(line_values[-3])
            irq_stat['steal'] = float(line_values[-4])
            irq_stat['soft'] = float(line_values[-5])
            irq_stat['irq'] = float(line_values[-6])
            irq_stat['iowait'] = float(line_values[-7])
            irq_stat['system'] = float(line_values[-8])
            irq_stat['nice'] = float(line_values[-9])
            irq_stat['user'] = float(line_values[-10])

            cpu_name = line_values[-11]
        except Exception as err:
            print(err, "-------  GetCmdMpstat")
            continue

        irq_data['data'][cpu_name] = irq_stat
    return irq_data


def cpu_softirq(response_lines):
    if len(response_lines) < 2:
            return {}
    try:
        # discard the first two lines
        response_lines.pop(0)
        response_lines.pop(0)
    except Exception as e:
        print(response_lines, "-------  GetCmdMpstat-I")
        return {}

    softirq_resp = []
    softirq_data = {}
    softirq_data['data'] = {}

    # print(response_lines)
    startIndex = 0
    for line in response_lines:
        if (line.strip() == ''):
            startIndex = startIndex + 1

        if startIndex < 2:
            continue
        elif startIndex > 2:
            break

        softirq_resp.append(line) 

    if len(softirq_resp) <= 1:
        return softirq_data

    softirq_resp.pop(0)
    softirq_resp.pop(0)
    for line in softirq_resp:
        line_values = line.split()

        softirq_stat = {}
        try:
            softirq_stat['HRTIMER'] = toDecimal(line_values[-2])
            softirq_stat['TASKLET'] = toDecimal(line_values[-4])
            softirq_stat['NET_RX'] = toDecimal(line_values[-7])
            softirq_stat['NET_TX'] = toDecimal(line_values[-8])

            cpu_name = line_values[1]
        except Exception as err:
            print(err, "-------  GetCmdMpstat-I")
            continue

        softirq_data['data'][cpu_name] = softirq_stat

    return softirq_data

def cpu_avgload(response_lines):
    response_data = {}
    # if options['debug']:
    #     response_data['rawResult'] = response_lines[:]
    #     response_data['lepd_command'] = 'GetProcLoadavg'
    
    response = response_lines[0].split(" ")

    # '0.00 0.01 0.05 1/103 24750
    # 'avg system load of 1 minute ago, 5 minutes ago, 15 minutes ago,
    # the fourth is A/B, A is the number of running processes
    # B is the total process count.
    # last number, like 24750 is the ID of the most recently running process.
    result_data = {
        'last1': toDecimal(response[0]),
        'last5': toDecimal(response[1]),
        'last15': toDecimal(response[2])
    }
    response_data['data'] = result_data
    return response_data

def memory_procrank(resultLines):
    procrankData = {}
    if (len(resultLines) == 0):
            return {}
    procrankData['data'] = {}
    procrankData['data']['procranks'] = {}
    headerLine = resultLines.pop(0)
    lineIndex = 0
    
    for line in resultLines:
        if (re.match( r'\W+-+\W+-+\W-+.*', line, re.M|re.I)):
            break
        lineValues = line.split()

        procrankData['data']['procranks'][lineIndex] = {}
        procrankData['data']['procranks'][lineIndex]['pid'] = lineValues.pop(0)
        procrankData['data']['procranks'][lineIndex]['vss'] = toDecimal(Decimal(Decimal(lineValues.pop(0)[:-1])))
        procrankData['data']['procranks'][lineIndex]['rss'] = toDecimal(Decimal(Decimal(lineValues.pop(0)[:-1])))
        procrankData['data']['procranks'][lineIndex]['pss'] = toDecimal(Decimal(Decimal(lineValues.pop(0)[:-1])))
        procrankData['data']['procranks'][lineIndex]['uss'] = toDecimal(Decimal(Decimal(lineValues.pop(0)[:-1])))

        procrankData['data']['procranks'][lineIndex]['cmdline'] = ' '.join([str(x) for x in lineValues])
        
        lineIndex += 1

        if(len(procrankData) >= 25):
            break
    
    # now parse from end, which contains summary info
    lastLine = resultLines[-1]
    procrankData['data']['sum'] = {}
    if (lastLine.startswith('RAM:')):
        lastLine = lastLine.replace("RAM:", '')
        lastLineValuePairs = lastLine.split(", ")
        for valuePair in lastLineValuePairs:
            keyValuePair = valuePair.split()
            
            keyName = keyValuePair[1].strip()
            keyValue = keyValuePair[0].strip()

            procrankData['data']['sum'][keyName + "Unit"] = keyValue[-1:]
            procrankData['data']['sum'][keyName] = toDecimal(Decimal(Decimal(keyValue[:-1])))

    xssSumLine = resultLines[-3].strip()
    if (xssSumLine.endswith('TOTAL')):
        xssValues = xssSumLine.split()
        
        ussTotalString = xssValues[-2]
        procrankData['data']['sum']['ussTotalUnit'] = ussTotalString[-1:]
        procrankData['data']['sum']['ussTotal'] = toDecimal(Decimal(Decimal(ussTotalString[:-1])))
        
        pssTotalString = xssValues[-3]
        procrankData['data']['sum']['pssTotalUnit'] = pssTotalString[-1:]
        procrankData['data']['sum']['pssTotal'] = toDecimal(Decimal(Decimal(pssTotalString[:-1])))
        
    return procrankData

def io_status(resultLines):
    result = {}
    for i in range(len(resultLines)):
        if (not resultLines[i].startswith('Device:')):
            continue
        else:
            result = resultLines[i:]
            break

    if not result:
        return {}

    headerline = result.pop(0)

    io_status = {
#        'lepdDuration': duration,
        'disks': {},
        'diskCount': 0,
        'ratio': 0
    }
    for line in result:
        if (line.strip() == ""):
            continue

        line_values = line.split()

        device_name = line_values[0]
        io_status['diskCount'] += 1
        io_status['disks'][device_name] = {}

        io_status['disks'][device_name]['rkbs'] = line_values[5]
        io_status['disks'][device_name]['wkbs'] = line_values[6]
        io_status['disks'][device_name]['ratio'] = line_values[-1]
        
        this_disk_ratio = toDecimal(line_values[-1])
        if this_disk_ratio > io_status['ratio']:
            io_status['ratio'] = this_disk_ratio
    response_data = {
        'data': io_status,
    }
    return response_data


def on_connect(client, userdata, flags, rc):
    client.subscribe('/+/monitor/+/raw')

def on_message(client, userdata, msg):
    subservice = msg.topic.split('/')[3]
    end = str.encode("lepdendstring")
    serverResponse = msg.payload.replace(end, str.encode(''))
    responseJsonDecoded = json.loads(serverResponse.decode())
    response_lines = split_to_lines(responseJsonDecoded['result'])
    # response_lines = responseJsonDecoded['result'].split('\n')
    if(subservice == 'cpu_stat'):
        data = cpu_stat(response_lines)
    elif subservice == 'cpu_softirq':
        data = cpu_softirq(response_lines)
    elif subservice == 'cpu_avgload':
        data = cpu_avgload(response_lines)
    elif subservice == 'memory_procrank':
        data = memory_procrank(response_lines)
    elif subservice == 'io_status':
        data = io_status(response_lines)
    if(data):
        topic = msg.topic[:-4]
        client.publish(topic, json.dumps(data, ensure_ascii=False))

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set('monitor', 'hellomonitor')
client.tls_set(ca_certs='/code/site/app/modules/ca.crt')
client.connect('222.201.144.236', 8883, 60)
client.loop_forever()
