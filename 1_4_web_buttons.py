from machine import Pin
import network
import socket
import select

# LED setup
led = Pin(4, Pin.OUT)

# Wi-Fi setup
ssid = 'Your-WiFi'
password = 'Your-Password'

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while not wlan.isconnected():
        pass
    print('Wi-Fi connected, see website at:', wlan.ifconfig()[0])

# HTML page
html = """
<!DOCTYPE html>
<html>
<body style='text-align:center;'>
    <h1>Toggle LED</h1>
    <form action='/on'><button><h2>Turn ON</h2></button></form>
    <form action='/off'><button><h2>Turn OFF</h2></button></form>
</body>
</html>
"""

# Web server
def start_server():
    server = socket.socket()
    server.bind(('', 80))
    server.listen(5)
    server.setblocking(False)
    print('Server running...')
    return server

def handle_client(s):
    try:
        request = s.recv(1024).decode()
        if '/on' in request:
            led.on()
        elif '/off' in request:
            led.off()
        s.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n" + html)
    except Exception as e:
        print(f'Error: {e}')
    finally:
        s.close()

# Main loop
connect_wifi()
server = start_server()

connections = [server]
while True:
    readable, _, _ = select.select(connections, [], [])
    for s in readable:
        if s is server:
            conn, _ = server.accept()
            conn.setblocking(False)
            connections.append(conn)
        else:
            handle_client(s)
            connections.remove(s)
