#!python.exe
# -*- coding: utf-8 -*-
from json import loads
from sys import _getframe
from os import path
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from configuration import SetMyLogger, ConnectMqtt, Topic
GUI=True

if GUI:
    import PySimpleGUI as sg
    states_list_column = [
        [sg.Listbox(values=[], enable_events=True, size=(30, 15), key="-STATUS LIST-")]
    ]

    image_viewer_column = [
        [sg.Image(filename='OriginalImages/Image.png', key="-IMAGE-", size=(240, 240))]
    ]

    layout = [
            [sg.TabGroup(
                [[
                sg.Tab('Actual Status', image_viewer_column), 
                sg.Tab('Old Status', states_list_column)
                ]]
            )],
            [sg.Button('Export'), sg.Button('Config')],
            ]

    window = sg.Window("Status Receiver", layout)
    StatusList=[]

def TellMeNow():
	from datetime import datetime
	return str(datetime.now().strftime("%Y%m%d%H%M%S"))

def Subscribe(client):
    def OnMessage(client, userdata, IncomingMessage):
        DefName=_getframe( ).f_code.co_name
        Message=IncomingMessage.payload.decode()
        Topic=IncomingMessage.topic
        logger.info(DefName+'(): Received '+str(Message)+' from topic {'+str(Topic)+'}')
        MessageDict=loads(Message)
        logger.debug(DefName+'(): Dictionary='+str(MessageDict))
        if GUI:
            StatusText=''
            for MessageItem in MessageDict:
                StatusText+=str(MessageItem)+':'+str(MessageDict[MessageItem])+';'
            StatusList.append(str(StatusText)+TellMeNow())
            window["-STATUS LIST-"].update(StatusList)
            GenerateImage(MessageDict)
            window["-IMAGE-"].update(filename='ToPublish/image.png')
    client.subscribe(Topic)
    client.on_message = OnMessage

def GenerateImage(MessageDict):
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

def main():
    global logger
    logger = SetMyLogger(path.basename(__file__))
    DefName=_getframe( ).f_code.co_name
    logger.debug(DefName+': Logging active for me: '+str(path.basename(__file__)))
    client = ConnectMqtt(logger)
    Subscribe(client)
    #client.loop_forever()
    while True:
        client.loop_start()
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
    window.close()
    client.disconnect()
    client.loop_stop()

if __name__ == '__main__':
    main()