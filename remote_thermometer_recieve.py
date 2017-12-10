import bluetooth

server_sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM )

port = 1
server_sock.bind(("",port))
server_sock.listen(1)

client_sock,address = server_sock.accept()
print "Accepted connection from ",address

while(1):
    data = ""
    data_valid = False
    try:
        data = client_sock.recv(1024)
        data_valid = True
    except bluetooth.btcommon.BluetoothError:
        print("Bluetooth recieve error")
    print "received [%s]" % data

client_sock.close()
server_sock.close()
