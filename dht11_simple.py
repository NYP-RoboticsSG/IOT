from machine import Pin  from time import sleep  import dht
sensor = dht.DHT11(Pin(4))  
while True:
	sensor.measure()
	temp = sensor.temperature()  
	hum = sensor.humidity()
	print(“Temperature: {}°C Humidity: {}% ”. format(temp, hum))  
	sleep(2)
