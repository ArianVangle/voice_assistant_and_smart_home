import asyncio
from kasa import Discover
from kasa import Module
import kasa
import kasa.feature
import kasa.module

ip_mama = '172.20.10.3'
ip_home = "192.168.1.123"
async def turn(state):
    dev = await Discover.discover_single(ip_home, username="ariansemenoff@yandex.ru", password="Arian1310!")
    await dev.update()
    light = dev.modules[Module.Light]

    if state==1: await dev.turn_on()
    elif state==0: await dev.turn_off()
    elif state==2: await light.set_hsv(145,77,80) #green
    elif state==3: await light.set_hsv(5,92,94) #red
    elif state==5: await light.set_hsv (241,95,87) #blue
    elif state==4: await dev.features.get("color_temperature").set_value(5800)
    elif state==6: await light.set_hsv (61,81,93) #yellow

 
