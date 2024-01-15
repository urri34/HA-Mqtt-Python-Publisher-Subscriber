#!python.exe
# -*- coding: utf-8 -*-
from random import randint
from os import path
from sys import stdin, stdout, _getframe
from paho.mqtt import client as mqtt_client
from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL
LogToFile = 1
LogFile=path.dirname(__file__).replace('\\','/')+'/DisplayState.log'
LogLevel=INFO #.DEBUG .INFO .WARNING .ERROR .CRITICAL

Broker = '192.168.1.11'
Port = 1883
Topic = "display/state"
ClientId = f'python-mqtt-tcp-pub-sub-{randint(0, 1000)}'
UserName = 'mqtt'
Password = 'mqtt'
RetryConnectionTime = 5
PublishRepetitionTime = 10
WaitForLoopTime = 1

def SetMyLogger(MyName):
	from  logging import basicConfig, FileHandler, StreamHandler, getLogger
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