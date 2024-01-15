#!python.exe
# -*- coding: utf-8 -*-
import json
from sys import _getframe
from os import path
from configuration import SetMyLogger, ConnectMqtt, Topic

def subscribe(client):
    def OnMessage(client, userdata, IncomingMessage):
        DefName=_getframe( ).f_code.co_name
        Message=IncomingMessage.payload.decode()
        Topic=IncomingMessage.topic
        logger.debug(DefName+'(): Received '+str(Message)+' from topic {'+str(Topic)+'}')
        MessageDict=json.loads(Message)
        logger.info(DefName+'(): Dictionary='+str(MessageDict))
    client.subscribe(Topic)
    client.on_message = OnMessage

def main():
    global logger
    logger = SetMyLogger(path.basename(__file__))
    DefName=_getframe( ).f_code.co_name
    logger.debug(DefName+': Logging active for me: '+str(path.basename(__file__)))
    client = ConnectMqtt(logger)
    subscribe(client)
    client.loop_forever()

if __name__ == '__main__':
    main()