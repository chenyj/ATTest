# -*-coding:utf8-*-
'''
通过串口操作M5310进行网络测试
Created on 5-26-2018
@author: 陈永吉
'''

import os
import re
import time
#import httplib2
import serial


def main():
    #AT指令
    getIMSI = 'AT+CIMI\r\n'
    getAPN = 'AT+CGDCONT?\r\n'
    detached = 'AT+CGATT=0\r\n'
    attached = 'AT+CGATT=1\r\n'
    getLocalIP = 'AT+CGPADDR\r\n'
    pingTest = 'AT+NPING="'

    TIMEFORMAT='%Y%m%d%H%M%S'

    try:
        ser = serial.Serial('COM3', 9600, timeout=1)    #串口COM3在不同PC上有可能不同，需根据设备管理器里的标识进行修改
    except:
        print('串口异常，请检查是串口否被占用或者连接是否正常！')
        exit()

    if ser.isOpen():
        print("------------串口连接成功------------")
        ser.write(getIMSI.encode())
        IMSI = "".join(re.findall('[0-9]', str(ser.readall()))) #IMSI号码
        print('IMSI号码：' + IMSI)
        ser.write(attached.encode())
        ser.write(getAPN.encode())        
        APN = str(ser.readall()).split(',')[2]  #建立承载使用的APN
        print('建立承载使用的APN：' + APN)

        if APN is None:
            print('PDP激活中，请稍后再试')
            ser.close()
            exit()

        with open('log.csv', 'w') as log:
            #log.truncate()
            log.write(',ISMI号码:' + IMSI + ',APN:' + APN + '\n')
            log.write('序号,本地IP,目的地址,测试结果\n')

        pdpAttachTimes = input('输入重新建立承载次数:')
        targetIP = input('输入ping测的目的地址(多个地址以\';\'分割)：')
        targetIPList = list(set(re.split(';|；', targetIP)))

        count = 0
        while count < int(pdpAttachTimes):
            count += 1
            print('------------第' + str(count) + '次ping测试------------')

            #附着入网
            ser.write(attached.encode())
            time.sleep(1)            
            print('附着网络...' + str(ser.readall()).split('\\r\\n')[1])

            #获取终端IP地址
            print('获取IP地址中...')
            ser.write(getLocalIP.encode())
            getLocalIPResult = str(ser.readall())
            retryTimes = 0
            while re.search(',', getLocalIPResult) is None:
                ser.write(getLocalIP.encode())
                getLocalIPResult = str(ser.readall())
                time.sleep(1)
                retryTimes += 1
                if retryTimes > 10:
                    print('无法获取IP地址，程序自动退出！')
                    ser.close()
                    exit()
            localIP = getLocalIPResult.split(',')[1].split('\\')[0] #格式化后的本地IP地址
            print('本地IP地址：' + localIP)

            #进行ping测试
            for i in range(0, len(targetIPList)):
                pingIPAddress = pingTest + targetIPList[i] + '",,4000\r\n'
                ser.write(pingIPAddress.encode())
                time.sleep(5)  #PING测命令里设定ping测超时时间为4秒，所以需等待5S获取ping测超时信息
                pingResultDetailList = str(ser.readall()).split('\\r\\n')
                #print(pingResultDetailList)
                if len(pingResultDetailList) > 3:
                    if re.search('NPINGERR:', pingResultDetailList[3]) is None:
                        print('Ping测地址:' + targetIPList[i] + ' 成功，目的可达！')
                        print(pingResultDetailList[6])
                        print(pingResultDetailList[7])
                        pingResult = 'Success'
                    elif re.search('NPING:', pingResultDetailList[3]) is None:
                        print('Ping测地址:' + targetIPList[i] + ' 失败，目的地址不可达！')
                        pingResult = 'Failure'
                else:                     
                    print('模块内部错误，程序自动退出！')
                    ser.close()
                    exit()
                with open('log.csv', 'a+') as log:
                    log.write(str(count) + ',' + localIP + ',' + targetIPList[i] + ',' + pingResult + '\n')

            ser.write(detached.encode())
            print('终端去附着：' + str(ser.readall()).split('\\r\\n')[1])
            time.sleep(1)

        ser.close()
        os.rename('log.csv','log' + str(time.strftime(TIMEFORMAT)) + '.csv')
    else:
        print("串口连接失败！")

#获取承载终端的局点信息。M5310由于不支持HTTP协议，以及ICMP协议支持不完整，因此没调用以下方法
'''
def getAttachCenter(IPAddress):
    http = httplib2.Http()
    host = 'http://freeapi.ipip.net/'
    requestHost = host + str(IPAddress)
    response,content = http.request(requestHost, 'GET')
    attachCenter = content.decode('utf-8').split('","')[2]
    #print(attachCenter)
    return attachCenter
'''




if __name__ == '__main__':
    main()
