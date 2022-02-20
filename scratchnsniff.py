import pyshark
import socket
import argparse
import sys

# Instantiate the parser
parser = argparse.ArgumentParser(description='Scratch\'n\'Sniff - Remote Packet Capture Agent')
parser.add_argument('--dstip', type=str, required=True, help='IP to forward traffic to')
parser.add_argument('--dstport', type=int, required=False, help='Port to forward traffic to')
parser.add_argument('--packetfilter', type=str, required=False, help='TCPDump formatted Capture Filter')
parser.add_argument('--interface', type=str, required=True, help='Interface to capture on')

args = parser.parse_args()

dest_ip = str(args.dstip)
if args.dstport == None:
    dest_port = 37008   #Set Default Port if none specified
else:
    dest_port = int(args.dstport)
packet_filter = str(args.packetfilter)
interface = str(args.interface)

print("Scratch\'n\'Sniff - Remote Packet Capture Agent")

if interface == 'any':
    print("Error: Using interface \"any\" is not supported. It makes pyshark confused and breaks things.")
    print("Please specify a an interface to capture on, or if you're handy, take a look at fixing this!")
    sys.exit()

if packet_filter == 'None':
    packet_filter = ''
    print("Capturing and forwarding all traffic on interface " + str(interface))
else:
    print("Forwarding all traffic matching filter " + str(packet_filter) + " on interface " + str(interface))
print("To remote host " + str(dest_ip) + " on UDP port " + str(dest_port))

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def TZSP_Encap(data):
    data = data.hex()                #Convert to Hex
    return '0100000101' + data       #Append TZSP Header

def Forward(data):
    data = TZSP_Encap(data)         #Add TZSP Header
    #Send it
    sock.sendto(bytes.fromhex(data), (dest_ip, dest_port))
    return

count = 1
print("Starting capture...")
capture = pyshark.LiveCapture(interface=interface, bpf_filter=packet_filter, include_raw=True, use_json=True)
for packet in capture.sniff_continuously():
    Forward(packet.get_raw_packet())
    print("Forwarded " + str(count) + " matching packets to remote host.", end='\r')
    count += 1

