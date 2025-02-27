import network
import time

def connect_to(ssid, passwd):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, passwd)  

    while not wlan.isconnected():
        time.sleep(1)
    
    return wlan.ifconfig()
