
import logging
logging.basicConfig(level=logging.DEBUG)
import pyshark
import socket
import os
import argparse
import sys

# Instantiate the parser
##parser = argparse.ArgumentParser(description='Scratch\'n\'Sniff - Remote Packet Capture Agent')
##parser.add_argument('--destination', type=str, required=True, help='IP to forward traffic to')
##parser.add_argument('--packet filter', type=str, required=False, help='TCPDump formatted Capture Filter')
##
##args = parser.parse_args()

# bind_ip = str(args.bind_ip)
# rtp_destination = str(args.rtp_destination)
# rtp_port = int(args.rtp_port)
# rtp_payload_id = int(args.rtp_payload_id)

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

capture = pyshark.LiveCapture(interface='any', bpf_filter=packet_filter, include_raw=True, use_json=True)
logging.debug("Starting capture...")
for packet in capture.sniff_continuously():
    print('Just arrived:' + str(packet))
    Tx(packet.get_raw_packet())

    
