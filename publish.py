#!python.exe
# -*- coding: utf-8 -*-
from json import dumps
from time import sleep
from random import randint
from os import path
from sys import _getframe
from configuration import SetMyLogger, ConnectMqtt, Topic, PublishRepetitionTime, WaitForLoopTime
DoItForEver=True

def publish(client, MessageDict):
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
    sleep(WaitForLoopTime)
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
            publish(client, MessageDict)
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