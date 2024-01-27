#!python.exe
# -*- coding: utf-8 -*-
from json import loads
from os import path
from sys import _getframe
from os import path
from time import sleep
from sys import stdin, stdout, _getframe
from paho.mqtt import client as mqtt_client
import PySimpleGUI as sg
from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL
from configuration import Topic, ClientId, UserName, Password, Broker, Port, RetryConnectionTime, PublishRepetitionTime

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

def ConnectMqtt() -> mqtt_client:
    def OnConnect(client, userdata, flags, rc):
        DefName=_getframe( ).f_code.co_name
        logger.info(DefName+'(): Succesfully connected to Mqtt broker')

    def OnDisconnect(client, userdata, rc):
        DefName=_getframe( ).f_code.co_name
        logger.info(DefName+'(): Disconnecting from Mqtt broker')

    DefName=_getframe( ).f_code.co_name
    client = mqtt_client.Client(ClientId)
    client.username_pw_set(UserName, Password)
    client.on_connect = OnConnect
    try:
        client.connect(Broker, Port, keepalive=120)
        logger.info(DefName+'(): Succesfully connected to Mqtt broker')
    except:
         logger.info(DefName+'(): Unable to connected to Mqtt broker')
    client.on_disconnect = OnDisconnect
    return client

def TellMeNow():
	from datetime import datetime
	return str(datetime.now().strftime("%Y/%m/%d %H:%M:%S"))

def Subscribe(client):
    def OnMessage(client, userdata, IncomingMessage):
        global StatusList, window_main
        DefName=_getframe( ).f_code.co_name
        Message=IncomingMessage.payload.decode()
        Topic=IncomingMessage.topic
        logger.info(DefName+'(): Received '+str(Message)+' from topic {'+str(Topic)+'}')
        MessageDict=loads(Message)
        logger.debug(DefName+'(): Dictionary='+str(MessageDict))
        StatusText=''
        for MessageItem in MessageDict:
            StatusText+=str(MessageItem)+':'+str(MessageDict[MessageItem])+';'
        StatusList.insert(0, str(StatusText)+TellMeNow())
        window_main["-STATUS LIST-"].update(StatusList)
        GenerateImage(MessageDict)
        window_main["-IMAGE-"].update(filename='ToPublish/image.png')

    global StatusList, window
    StatusList=[]
    if client.is_connected():
        client.subscribe(Topic)
        client.on_message = OnMessage

def GenerateImage(MessageDict):
    from PIL import Image
    from PIL import ImageDraw
    from PIL import ImageFont
    Status = int(MessageDict['Status'])
    match Status:
        case 1:
            MyImage = Image.open('OriginalImages/Image1.png')
        case 0:
            MyImage = Image.open('OriginalImages/Image0.png')
        case _:
            MyImage = Image.open('OriginalImages/Image.png')
    I1 = ImageDraw.Draw(MyImage)
    myFont = ImageFont.truetype('OriginalImages/Typo_Round_Bold_Demo.otf', 50)
    I1.text((10, 10), MessageDict['Element'], font=myFont, fill=(255, 255, 255))
    MyImage.save("ToPublish/image.png")

def OpenExportWindow():
    layout_export = [[
    sg.Text('Exported to '+str(path.splitext(path.basename(__file__))[0]+'.log'))
    ]]
    window_export = sg.Window("Export Window", layout_export)
    window_export.read()

def OpenMainWindows():
    global StatusList, window_main
    states_list_column = [
        [sg.Listbox(values=[], enable_events=True, size=(30, 15), key="-STATUS LIST-", horizontal_scroll=True)]
    ]

    image_viewer_column = [
        [sg.Image(filename='OriginalImages/Image.png', key="-IMAGE-", size=(240, 240))]
    ]
    layout_main = [
            [sg.TabGroup(
                [[
                sg.Tab('Actual Status', image_viewer_column), 
                sg.Tab('Old Status', states_list_column)
                ]]
            )],
            [sg.Button('Export')],
            ]
    window_main = sg.Window("Status Receiver", layout_main)
    while True:
        Event, values = window_main.read()
        if Event == "Exit" or Event == sg.WIN_CLOSED:
            break
        if Event == "Export":
            file1 = open(path.splitext(path.basename(__file__))[0]+'.log', 'w')
            for Line in StatusList:
                file1.write(Line+'\n')
            file1.close()
            OpenExportWindow()

def OpenConnectionWindows():
    global Broker, UserName, Password, client, window_connection
    DefName=_getframe( ).f_code.co_name
    logger.debug(DefName+'(): Opening connection window')
    layout_connection=[
            [sg.Text("Configuration")],
            [sg.Text("Broker"),sg.InputText(Broker, key='Broker', size=(25, 20))],
            [sg.Text("Username"),sg.InputText(UserName, key='UserName', size=(22, 20))],
            [sg.Text("Password"),sg.InputText(Password, key='Password', size=(22, 20))],
            [sg.Button('Apply'), sg.Button('Exit')],
            [sg.HSep()],
            [sg.Text("Next try in ...")],
            [sg.ProgressBar(RetryConnectionTime*10, orientation='h', size=(18, 20), key='progressbar')],
            [sg.Listbox(values=[], enable_events=True, size=(30, 15), key="-CONNECTION-")]]
    window_connection = sg.Window("Connection", layout_connection)
    logger.debug(DefName+'(): First even read at connection window')
    Event = window_connection.read(50)
    StatusList=[]
    StatusList.append("Trying on "+str(TellMeNow())+'...')
    StatusList.append("Broker="+str(Broker))
    StatusList.append("UserName="+str(UserName))
    StatusList.append("Password="+str(Password))
    StatusList.append("Port="+str(Port))
    StatusList.append("ClientId="+str(ClientId))
    StatusList.append("RetryConnectionTime="+str(RetryConnectionTime))
    StatusList.append("PublishRepetitionTime="+str(PublishRepetitionTime))
    logger.debug(DefName+'(): Updating StatusList at connection window')
    window_connection["-CONNECTION-"].update(StatusList)
    logger.debug(DefName+'(): Full progress bar at connection window ('+str(RetryConnectionTime*10)+')')
    window_connection['progressbar'].UpdateBar(RetryConnectionTime*10)
    logger.debug(DefName+'(): Second even read at connection window')
    Event = window_connection.read(50)
    BreakMeMyFriend=False
    while True:
        logger.debug(DefName+'(): Prepare mqtt connection')
        client = PrepareConnection()
        if client.is_connected():
            return True
        window_connection['progressbar'].UpdateBar(0)
        for Iteration in range(RetryConnectionTime*10):
            Event, Values = window_connection.read(100)
            if Event == "Exit" or Event == sg.WIN_CLOSED:
                BreakMeMyFriend=True
            if Event == "Apply":
                logger.debug("New value for Broker="+str(Values['Broker']))
                Broker=Values['Broker']
                logger.debug("New value for UserName="+str(Values['UserName']))
                UserName=Values['UserName']
                logger.debug("New value for Password="+str(Values['Password']))
                Password=Values['Password']
            logger.debug(DefName+'(): Increment progress bar at connection window ('+str(Iteration + 1)+')')
            window_connection['progressbar'].UpdateBar(Iteration + 1)
        if BreakMeMyFriend:
            window_connection.close()
            return 0
        else:
            StatusList.insert(0, "-----------------------------------")
            StatusList.insert(0, "PublishRepetitionTime="+str(PublishRepetitionTime))
            StatusList.insert(0, "RetryConnectionTime="+str(RetryConnectionTime))
            StatusList.insert(0, "ClientId="+str(ClientId))
            StatusList.insert(0, "Port="+str(Port))
            StatusList.insert(0, "Password="+str(Password))
            StatusList.insert(0, "UserName="+str(UserName))
            StatusList.insert(0, "Broker="+str(Broker))
            StatusList.insert(0, "Trying on "+str(TellMeNow())+'...')
            logger.debug(DefName+'(): Updating StatusList at connection window')
            window_connection["-CONNECTION-"].update(StatusList)

def PrepareConnection():
    client = ConnectMqtt()
    client.loop_start()
    sleep(0.3)
    return client

def main():
    global logger, StatusList, Broker, UserName, Password, client, window_connection
    
    logger = SetMyLogger(path.basename(__file__))
    DefName=_getframe( ).f_code.co_name
    logger.debug(DefName+'(): Logging active for me: '+str(path.basename(__file__)))

    if OpenConnectionWindows():
        logger.debug(DefName+'(): Going to subscribe')
        Subscribe(client)
        logger.debug(DefName+'(): Closing connection window')
        window_connection.close()
        logger.debug(DefName+'(): Opening main window')
        OpenMainWindows()

    if client.is_connected():
        logger.debug(DefName+'(): Disconnecting and stoping loop')
        client.disconnect()
        client.loop_stop()

if __name__ == '__main__':
    main()