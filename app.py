from boot import connect_to
from microdot import Microdot
from machine import Pin, ADC, SoftI2C

import neopixel
import ds18x20
import ssd1306
import onewire
import time

# Default address 0x3C and default pins
i2c = SoftI2C(sda=Pin(21), scl=Pin(22))
display = ssd1306.SSD1306_I2C(128, 32, i2c)

# DS18B20 temperature sensor
ds_sensor = ds18x20.DS18X20(onewire.OneWire(Pin(19)))
roms = ds_sensor.scan()

# LDR an AD channel
ldr = ADC(Pin(39))

# Buzzer output pin
buzzer = Pin(14, Pin.OUT)

# Individual LEDs
ledr = Pin(32, Pin.OUT)
ledy = Pin(33, Pin.OUT)
ledg = Pin(25, Pin.OUT)

# Buttons
left = Pin(13, Pin.IN)
enter = Pin(15, Pin.IN)
right = Pin(23, Pin.IN)

# Neopixel for RGB WS2818
rgb = neopixel.NeoPixel(Pin(27), 4)

# Connect to WiFi
ifconfig = connect_to("<SSID>", "<PASSWD>")
# Show IP address on display
display.text("Running in...", 0, 0, 1)
display.text(ifconfig[0], 0, 16, 1)
display.show()

# Create Microdot app instance
app = Microdot()

# Middleware for CORS
@app.after_request
def add_cors_headers(request, response):
    # Allow from every origin
    response.headers['Access-Control-Allow-Origin'] = '*'  # Permite cualquier origen
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'  # Métodos permitidos
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'  # Encabezados permitidos
    return response

@app.route('/')
def getAll(request):
    global ledr, ledy, ledg, rgb, buzzer, left, enter, right
    
    return {
        "leds": [bool(ledr.value()), bool(ledy.value()), bool(ledg.value())],
        "rgb": {"r": rgb[0][0], "g": rgb[0][1], "b": rgb[0][2] },
        "buzzer": bool(buzzer.value()),
        "buttons": {"left": bool(left.value()), "enter": bool(enter.value()), "right": bool(right.value())}
    }

@app.route('/led/<string:color>/<int:value>')
def setLedState(request, color, value):
    global ledr, ledy, leg
    
    if color == "red":
        ledr.value(value)
    elif color == "yellow":
        ledy.value(value)
    elif color == "green":
        ledg.value(value)
    
    return {"status": 200}

@app.route('/buzzer/<int:value>')
def setBuzzerState(request, value):
    global buzzer
    buzzer.value(value)
    return {"status": 200}

@app.route('/rgb')
def setRGB(request):
    global rgb
    
    r = request.args.get('r', default=0)
    g = request.args.get('g', default=0)
    b = request.args.get('b', default=0)
    
    r = int(r)
    g = int(g)
    b = int(b)
    
    for i in range(4):
        rgb[i] = (r, g, b)
    
    rgb.write()
    
    return {"status": 200}

@app.route('/temperature')
def getTemperature(request):
    global ds_sensor, roms
    
    if not roms:
        return None
    
    ds_sensor.convert_temp()
    time.sleep_ms(1)
    temp = ds_sensor.read_temp(roms[0])
    return {"temperature": ds_sensor.read_temp(roms[0])}

@app.route('/lux')
def getLux(request):
    global ldr
    lux = 0
    
    for _ in range(10):
        lux += ldr.read_u16()
        
    lux /= 10
    lux = lux * 100 / 65535
        
    return {"lux": lux}


@app.route('/buttons')
def getButtons(request):
    global left, enter, right
    
    return {"buttons": {"left": bool(left.value()), "enter": bool(enter.value()), "right": bool(right.value())}}

app.run(port=80, host="0.0.0.0")
