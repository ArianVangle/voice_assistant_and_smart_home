import asyncio
from kasa import Discover
from kasa import Module
import kasa
import kasa.feature
import kasa.module


# async def turn(state):
#     dev = await Discover.discover_single("192.168.1.123", username="ariansemenoff@yandex.ru", password="Arian1310!")

#     await dev.turn_on()
#     await dev.update()
#     #получение всех вохможных параметров лампы
#     for feature_id, feature in dev.features.items():
#         print(f"{feature.name} ({feature_id}): {feature.value}")
#     # print(dev.features.items())
#     await dev.features.get("color_temperature").set_value(5800)
#     light = dev.modules[Module.Light]
#     await light.set_brightness(100)
#     # print(light)
#     await light.set_hsv(181, 94, 92)
#     await light.set_hsv(313, 94, 92)
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
    elif state==6: await light.set_hsv (61,81,93)
    # await dev.update()





# asyncio.run(turn(0))
# print(1000)

 