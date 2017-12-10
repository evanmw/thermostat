
import bluetooth
import time

BD_ADDR = "B8:27:EB:8B:68:DA"
PORT = 1
SAMPLE_FREQ = 60 # Hz

sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM )
sock.connect((BD_ADDR, PORT))

while (1):
    try:
        sock.send("68")
    except bluetooth.btcommon.BluetoothError:
        print ("Bluetooth error")
    time.sleep(60/SAMPLE_FREQ)

sock.close()