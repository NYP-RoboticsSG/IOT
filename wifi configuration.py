import network
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect('Tertiary infotech', 'Tertiary888')
#wlan.connect('thef_home', 'kzbev83544')
print(wlan.ifconfig()[0])
