import requests
import json
import time


def send_mesagge(msg, sender, port):
    url = 'http://localhost:'+str(port)+'/webhooks/rest/webhook'
    data = {"sender": sender, "message": msg} 
    x = requests.post(url, json=data) 
    rta = x.json() 
    if x.status_code == 200: 
        return rta.pop(0)['text'] 
    else: 
        print(x.raw) 
        return None 

"""
    INSTANCIO EL BOT 1
"""

p1 = 5005 
s1 = 'Bot 1'

"""
    INSTANCIO EL BOT 2
"""

p2 = 5006 
s2 = 'Bot 2' 

message = 'Hola, como estas?'
print(s1 + ': ' + message)
while True: 
    message = send_mesagge(message, s1, p2) 
    print(s2 + ': ' + message)
    time.sleep(1)
    message = send_mesagge(message, s2, p1) 
    print(s1 + ': ' + message)
    time.sleep(1)
