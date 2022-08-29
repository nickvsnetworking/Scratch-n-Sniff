import pyshark
import sys
import socket

dest_ip = '10.0.1.252'
dest_port = 37008
packet_filter = 'port 5060'

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tzsp_header= '0100000101'

def TZSP_Encap(data):

    eth_header = data[0:14].hex()

    #Convert to Hex
    data = data.hex()
    #Ethernet Header
    
    print("eth_header: " + str(eth_header))

    #Append TZSP Header
    return tzsp_header + data

def Tx(data):
    #Add TZSP Header
    data = TZSP_Encap(data)
    #Send it
    sock.sendto(bytes.fromhex(data), (dest_ip, dest_port))
    print("Sent!")
    return

capture = pyshark.LiveCapture(interface='enp0s25', bpf_filter='', include_raw=True, use_json=True)
for packet in capture.sniff_continuously():
    print('Just arrived:' + str(packet))
    Tx(packet.get_raw_packet())
    print("Sent!")

