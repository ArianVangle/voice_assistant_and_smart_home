import subprocess



p1 = subprocess.Popen(['py', 'EVA_4_1.py'])
p2 = subprocess.Popen(['py', 'bot.py'])



p1.wait()
p2.wait()