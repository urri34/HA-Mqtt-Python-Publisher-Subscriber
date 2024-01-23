#!python.exe
# -*- coding: utf-8 -*-
from json import loads
from os import path
from sys import _getframe
from os import path
from sys import stdin, stdout, _getframe
from paho.mqtt import client as mqtt_client
from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL
from configuration import Topic, ClientId, UserName, Password, Broker, Port

LogToFile = 1
LogFile=path.dirname(__file__).replace('\\','/')+'/Cli_Mqtt_Pub_Subs.log'
LogLevel=DEBUG #.DEBUG .INFO .WARNING .ERROR .CRITICAL

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

def Subscribe(client):
    def OnMessage(client, userdata, IncomingMessage):
        DefName=_getframe( ).f_code.co_name
        Message=IncomingMessage.payload.decode()
        Topic=IncomingMessage.topic
        logger.info(DefName+'(): Received '+str(Message)+' from topic {'+str(Topic)+'}')
        MessageDict=loads(Message)
        logger.debug(DefName+'(): Dictionary='+str(MessageDict))

    client.subscribe(Topic)
    client.on_message = OnMessage

def main():
    global logger
    logger = SetMyLogger(path.basename(__file__))
    DefName=_getframe( ).f_code.co_name
    logger.debug(DefName+': Logging active for me: '+str(path.basename(__file__)))
    client = ConnectMqtt(logger)
    Subscribe(client)
    client.loop_forever()

if __name__ == '__main__':
    main()