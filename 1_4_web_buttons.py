from machine import Pin
import network
import socket

# LED setup
led = Pin(2, Pin.OUT)

# Wi-Fi setup
ssid = 'Your-WIFI'
password = 'Your-PASSWORD'
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)
while not wlan.isconnected():
    pass
print('Wi-Fi connected, see website at:', wlan.ifconfig()[0])

# HTML website code
html = """
<!DOCTYPE html>
<html>
<body style='text-align:center;'>
    <h1>Toggle LED</h1>
    <form action='/on'><button>Turn ON</button></form>
    <form action='/off'><button>Turn OFF</button></form>
</body>
</html>
"""

# Start web server
server = socket.socket()
server.bind(('', 80))
server.listen(1)
print('Server running...')

# Handle web requests
while True:
    conn, _ = server.accept()
    request = conn.recv(1024).decode()
    led.on() if '/on' in request else led.off() if '/off' in request else None
    conn.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n" + html)
    conn.close()