from machine import Pin, PWM
import network
import socket
import select
import time

# LED setup (use PWM for brightness control)
led = PWM(Pin(4), freq=1000)  # Pin 4 with 1 kHz frequency
led.duty(0)  # Start with LED off aka low = 0

# Wi-Fi setup
ssid = 'Your-WiFi'
password = 'Your-Password'

def connect_wifi():
    """Connect to Wi-Fi with timeout."""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    timeout = 10  # 10 seconds timeout
    while not wlan.isconnected() and timeout > 0:
        time.sleep(1)
        timeout -= 1
    if wlan.isconnected():
        print('Wi-Fi connected. IP address:', wlan.ifconfig()[0])
    else:
        raise RuntimeError("Failed to connect to Wi-Fi. Check your credentials.")

# HTML page with slider for brightness control
html = """
<!DOCTYPE html>
<html>
<body style='text-align:center;'>
    <h1>Adjust LED Brightness</h1>
    <input type="range" min="0" max="1023" value="0" id="brightness" oninput="updateBrightness(this.value)">
    <p>Brightness: <span id="value">0</span></p>
    <script>
        let timeout;
        function updateBrightness(value) {
            document.getElementById('value').innerText = value;
            clearTimeout(timeout);
            timeout = setTimeout(() => {
                fetch('/brightness?value=' + value);
            }, 200);  // Debounce requests to reduce load
        }
    </script>
</body>
</html>
"""

# Web server setup
def start_server():
    """Start the web server."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('', 80))
    server.listen(5)
    server.setblocking(False)
    print('Server running...')
    return server

def handle_client(s):
    """Handle a single client request."""
    try:
        request = s.recv(1024).decode()
        if not request:
            return
        print("Request received:", request)

        # Handle brightness adjustment
        if '/brightness?value=' in request:
            try:
                value = int(request.split('/brightness?value=')[1].split(' ')[0])
                value = max(0, min(1023, value))  # Clamp value between 0 and 1023
                led.duty(value)  # Adjust LED brightness
                print(f"Set brightness to: {value}")
            except (ValueError, IndexError):
                print("Invalid brightness value in request.")
        
        # Respond with the HTML page
        response = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n" + html
        s.send(response)
    except Exception as e:
        print(f'Error handling client: {e}')
    finally:
        s.close()

# Main loop
try:
    connect_wifi()
    server = start_server()
    connections = [server]

    while True:
        try:
            readable, _, _ = select.select(connections, [], [])
            for s in readable:
                if s is server:
                    conn, addr = server.accept()
                    print(f"New connection from: {addr}")
                    conn.setblocking(False)
                    connections.append(conn)
                else:
                    handle_client(s)
                    connections.remove(s)
        except Exception as e:
            print(f"Error in main loop: {e}")
except Exception as e:
    print(f"Critical error: {e}")
    led.deinit()
