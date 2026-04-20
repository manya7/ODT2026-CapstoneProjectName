import network
import socket
from machine import Pin
import time

# ---------- WIFI ----------
ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid='Rotary-Dial', password='12345678')

print("Connect to WiFi: Rotary-Dial")
print("IP:", ap.ifconfig()[0])

# ---------- OUTPUT ----------
phone_number = ""
status = "Ready"

# 🔐 change this to your correct number
SECRET = "1234"

# ---------- LED ----------
led = Pin(2, Pin.OUT)

# ---------- HTML ----------
def webpage():
    html = """<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="refresh" content="1">
<style>
body {
    text-align: center;
    font-family: Arial;
    background: #111;
    color: white;
}
.screen {
    font-size: 40px;
    margin-top: 40px;
    border: 3px solid white;
    display: inline-block;
    padding: 20px 30px;
    min-width: 200px;
}
.status {
    margin-top: 20px;
    font-size: 20px;
    color: #0f0;
}
button {
    margin-top: 30px;
    font-size: 18px;
    padding: 10px 20px;
}
</style>
</head>
<body>
<h1>Rotary Dial</h1>

<div class="screen">{}</div>
<div class="status">{}</div>

<form action="/reset">
<button>Reset</button>
</form>

</body>
</html>
""".format(phone_number, status)

    response = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n" + html
    return response

# ---------- SERVER ----------
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
server = socket.socket()
server.bind(addr)
server.listen(1)
server.setblocking(False)

# ---------- ROTARY ----------
dial = Pin(14, Pin.IN, Pin.PULL_UP)

last_state = 1
pulse_count = 0
last_time = 0

MIN_GAP = 150
COUNT_TIME = 1200
PAUSE_TIME = 2000

mode = "WAIT"
start_time = 0
locked = False

# ---------- LOOP ----------
while True:

    # ---------- WEB HANDLING ----------
    try:
        client, addr = server.accept()
        request = client.recv(1024)

        if b"/reset" in request:
            phone_number = ""
            status = "Reset"
            led.value(0)

        client.send(webpage().encode())
        client.close()

    except:
        pass

    # ---------- ROTARY LOGIC ----------
    current = dial.value()
    now = time.ticks_ms()

    if mode == "WAIT":
        if last_state == 1 and current == 0:
            pulse_count = 1
            last_time = now
            start_time = now
            mode = "COUNT"
            locked = True

    elif mode == "COUNT":
        if not locked:
            if last_state == 1 and current == 0:
                gap = time.ticks_diff(now, last_time)
                if gap > MIN_GAP:
                    pulse_count += 1
                    last_time = now
                locked = True

        if current == 1:
            locked = False

        if time.ticks_diff(now, start_time) > COUNT_TIME:
            digit = pulse_count
            if digit == 10:
                digit = 0

            phone_number += str(digit)
            print("Digit:", digit)

            mode = "PAUSE"
            start_time = now

    elif mode == "PAUSE":
        if time.ticks_diff(now, start_time) > PAUSE_TIME:
            if len(phone_number) > 0:
                status = "Dialing..."

                if phone_number == SECRET:
                    status = "Access Granted"
                    led.value(1)
                elif len(phone_number) >= len(SECRET):
                    status = "Wrong Number"
                    led.value(0)

            mode = "WAIT"
            pulse_count = 0

    last_state = current

    time.sleep_ms(1)