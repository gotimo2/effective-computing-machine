from paramiko import * #pylint: disable=unused-wildcard-import
import dotenv
import os
import asyncio
import gpiozero
from gpiozero import LED, Button

global lamps
lamps = 0

global queuedUp
queuedUp = False


led1 = LED(17)
led2 = LED(27)
led3 = LED(22)
led4 = LED(26)

ledList = [led1, led2, led3]

button1 = Button(5)
button2 = Button(6)

def button1Pressed():
    print('button pressed')
    global lamps
    lamps += 1

button1.when_pressed = button1Pressed


client = SSHClient()
dotenv.load_dotenv()
password = os.environ.get('SSH_PASSWORD')
username = os.environ.get('SSH_USERNAME')
ip = os.environ.get('SSH_IP')
port = os.environ.get('SSH_PORT')

client.set_missing_host_key_policy(AutoAddPolicy())
client.connect(ip, port=port, username=username, password=password, allow_agent=False, look_for_keys=False,)

async def sendCommand():
    commandToSend = os.environ.get('COMMAND1')
    client.exec_command(commandToSend)

async def doTheThing():
    global lamps
    if lamps == 3:
        await sendCommand()
        await flashingLED(led4, 80)
        print('DOING IT')

def button2Pressed():
    print('button 2 pressed')
    global queuedUp
    queuedUp = True

button2.when_pressed = button2Pressed    

async def flashingLED(led, amount):
    for _ in range(0, amount):
        led.on()
        await asyncio.sleep(0.05)
        led.off()
        await asyncio.sleep(0.05)


async def reduceLamps():
    print('reduce lamp task created')
    global lamps
    while True:
        if lamps > 0:
            await asyncio.sleep(2.5)
            lamps -= 1
        await asyncio.sleep(0.1)

async def waitForQueue():
    print("waiting for queue")
    global queuedUp
    while True:
        if queuedUp == True:
            await doTheThing()
            queuedUp = False
        await asyncio.sleep(0.1)

async def lampLoop():
    print('lamp loop continued')
    global lamps
    while True:
        if lamps == 0:
            for led in ledList:
                led.off()
        elif lamps == 1:
            
            led1.on()
            led2.off()
            led3.off()
        elif lamps == 2:
            
            led1.on()
            led2.on()
            led3.off()
        elif lamps == 3:
            for led in ledList:
                led.on()
        elif lamps < 3:
            lamps = 3
        await asyncio.sleep(0.1)
        
    
loop = asyncio.get_event_loop()
loop.create_task(reduceLamps())
loop.create_task(lampLoop())
loop.create_task(waitForQueue())
loop.run_forever()