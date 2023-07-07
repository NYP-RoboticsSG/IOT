from machine import Pin
from time import sleep
from machine import Timer
from umqtt.simple import MQTTClient
import dht
import network
import time
import sys
import os

sensor = dht.DHT11(Pin(4))
led = Pin('LED', Pin.OUT)

WIFI_SSID     = 'xxxx' #To fill in the SSID
WIFI_PASSWORD = 'xxxx' #To fill in the WIFI password

# WIFI_SSID     = 'Tertiary infotech'
# WIFI_PASSWORD = 'Tertiary888'

random_num = int.from_bytes(os.urandom(3), 'little')
mqtt_client_id      = bytes('client_'+str(random_num), 'utf-8') # Just a random client ID

#Adafruit credientails

ADAFRUIT_IO_URL     = 'io.adafruit.com' 
ADAFRUIT_IO_USERNAME = "xxxxxx" #To fill in the adafruit IO Username from you account
ADAFRUIT_IO_KEY = "xxxxxxxxxxx" #To fill in the adafruit IO Key from you account

TEMP_FEED_ID      = 'temperature'
HUM_FEED_ID       = 'humidity'
TOGGLE_FEED_ID = 'LED'

def connect_wifi():
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    wifi.disconnect()
    wifi.connect(WIFI_SSID,WIFI_PASSWORD)
    if not wifi.isconnected():
        print('Connecting..')
        timeout = 0
        while (not wifi.isconnected() and timeout < 5):
            print(5 - timeout)
            timeout = timeout + 1
            time.sleep(1) 
    if(wifi.isconnected()):
        print('Connected!')
        print('IP: ', wifi.ifconfig()[0])
    else:
        print('Not connected!')
        sys.exit()
      
connect_wifi() # Connecting to WiFi Router 

client = MQTTClient(client_id=mqtt_client_id, 
                    server=ADAFRUIT_IO_URL, 
                    user=ADAFRUIT_IO_USERNAME, 
                    password=ADAFRUIT_IO_KEY,
                    ssl=False)

def connect_mqtt():
    try:
        print("Connecting to MQTT ...")
        client.connect()
        print("Connected to MQTT")
    except Exception as e:
        print('Could not connect to MQTT server {}{}'.format(type(e)._name_, e))
        sys.exit()

def cb(topic,msg):
    print('Received Data : Topic = {}, Msg={}'.format(topic,msg))
    received_data = str(msg, 'utf-8')
    #print(received_data)
    if received_data == "ON" :
        led.on()
    if received_data == "OFF" :
        led.off()
    
connect_mqtt()
# Feed
temp_feed = bytes('{:s}/feeds/{:s}'.format(ADAFRUIT_IO_USERNAME, TEMP_FEED_ID), 'utf-8') # format - ~/feeds/temp
hum_feed = bytes('{:s}/feeds/{:s}'.format(ADAFRUIT_IO_USERNAME, HUM_FEED_ID), 'utf-8') # format - ~/feeds/hum
toggle_feed = bytes('{:s}/feeds/{:s}'.format(ADAFRUIT_IO_USERNAME, TOGGLE_FEED_ID),'utf-8')

client.set_callback(cb)
client.subscribe(toggle_feed)

def sens_data(data):
    #led.toggle()
    sensor.measure()                    # Measuring 
    temp = sensor.temperature()         # getting Temp
    hum = sensor.humidity()				# getting humidity
    try:
        client.publish(temp_feed,    
                  bytes(str(temp), 'utf-8'),   # Publishing Temp feed to adafruit.io
                  qos=0)
    
        client.publish(hum_feed,    
                  bytes(str(hum), 'utf-8'),   # Publishing Hum feed to adafruit.io
                  qos=0) # qos 0 transparent no handhaking simple fast 
    except:
        connect_mqtt()
        return
    print("Temperature : ", str(temp))
    print("Humidity    : ", str(hum))
    print()
    
timer = Timer(-1)
timer.init(period=15000, mode=Timer.PERIODIC, callback = sens_data)

while True:
    try:
        client.check_msg()
    except:
        client.disconnect()
        sys.exit()
