#!python.exe
# -*- coding: utf-8 -*-
from json import dumps
from time import sleep
from random import randint
from os import path
from sys import _getframe
from os import path
from sys import stdin, stdout, _getframe
from paho.mqtt import client as mqtt_client
from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL
from configuration import Topic, PublishRepetitionTime, ClientId, UserName, Password, Broker, Port

LogToFile = 1
LogFile=path.dirname(__file__).replace('\\','/')+'/Cli_Mqtt_Pub_Subs.log'
LogLevel=DEBUG #.DEBUG .INFO .WARNING .ERROR .CRITICAL

DoItForEver=True

def SetMyLogger(MyName):
	from logging import basicConfig, FileHandler, StreamHandler, getLogger
	from os import isatty
	LogFormat = ('[%(asctime)s] %(levelname)-8s %(name)-12s %(message)s')
	if isatty(stdin.fileno()) and LogToFile == 1:
		basicConfig(level=LogLevel, format=LogFormat, handlers=[FileHandler(LogFile), StreamHandler(stdout)])
	elif isatty(stdin.fileno()):
		basicConfig(level=LogLevel, format=LogFormat, handlers=[StreamHandler(stdout)])
	elif LogToFile == 1:
		basicConfig(level=LogLevel,	format=LogFormat, handlers=[FileHandler(LogFile)])
	logger = getLogger(MyName)
	return logger

def ConnectMqtt(logger) -> mqtt_client:
    def OnConnect(client, userdata, flags, rc):
        DefName=_getframe( ).f_code.co_name
        logger.info(DefName+'(): Succesfully connected to Mqtt broker')

    def OnDisconnect(client, userdata, rc):
        DefName=_getframe( ).f_code.co_name
        logger.info(DefName+'(): Disconnecting from Mqtt broker')

    client = mqtt_client.Client(ClientId)
    client.username_pw_set(UserName, Password)
    client.on_connect = OnConnect
    client.connect(Broker, Port, keepalive=120)
    client.on_disconnect = OnDisconnect
    return client

def Publish(client, MessageDict) -> bool:
    DefName=_getframe( ).f_code.co_name
    logger.debug(DefName+'(): Dictionary='+str(MessageDict))
    Message = dumps(MessageDict)
    result = client.publish(Topic, Message)
    status = result[0]
    if status == 0:
        logger.info(DefName+'(): Send '+str(Message)+' to topic {'+str(Topic)+'}')
        return 0
    else:
        logger.error(DefName+'(): Failed to send message to topic {'+str(Topic)+'}')
        return 1

def PrepareConnection(logger):
    client = ConnectMqtt(logger)
    client.loop_start()
    sleep(1)
    return client

def CloseConnection(client):
    client.loop_stop()
    client.disconnect()

def main():
    global logger
    logger = SetMyLogger(path.basename(__file__))
    DefName = _getframe( ).f_code.co_name
    logger.debug(DefName+'(): Logging active for me: '+str(path.basename(__file__)))
    client = PrepareConnection(logger)
    while True:
        if client.is_connected():
            MessageDict = {
                'Element': 'WifiSolar',
                'Status': randint(0, 2)
            }
            Publish(client, MessageDict)
            if DoItForEver:
                logger.debug(DefName+'(): For ever loop, sleeping '+str(PublishRepetitionTime))
                sleep(PublishRepetitionTime)
            else:
                logger.debug(DefName+'(): Just one message, exiting')
                break
        else:
            logger.info(DefName+'(): client not connected, retrying ...')
            CloseConnection(client)
            PrepareConnection(logger)
    CloseConnection(client)

if __name__ == '__main__':
    main()