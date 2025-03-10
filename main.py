import subprocess


p1 = subprocess.Popen(['py', r'./EVA_4_1.py'])
p2 = subprocess.Popen(['py', r'./bot.py'])

p1.wait()
p2.wait()