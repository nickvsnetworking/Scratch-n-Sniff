import logging
logging.basicConfig(level=logging.DEBUG)
import pyshark
import socket
import os
import argparse
import sys
import yaml

# Local Capture agent for cylic packet capturing.
# Parameters such as maximum number of pcap files kept, source port and rotation size are defined in config.yaml

with open("config.yaml", 'r') as configFile:
    yamlConfig = (yaml.safe_load(configFile))

maxFilesize = yamlConfig.get("localCapture", {}).get("maxFilesize", "200000") # Default 200mb max file size
maxPcaps = yamlConfig.get("localCapture", {}).get("maxPcaps", "5") # Default max 5 pcaps
outputFile = yamlConfig.get("localCapture", {}).get("outputFile", "./localCapture.pcap") # Default to the local directory
portList = yamlConfig.get("localCapture", {}).get("portList", [])

#Include a port filter, if defined.
portFilter = ""
if portList:
    portFilter = ' or '.join(f'port {port}' for port in portList)
    portFilter = '-f ' + '"' + portFilter + '"'

os.system(f'dumpcap -i any -w {outputFile} -b filesize:{maxFilesize} -b files:{maxPcaps} {portFilter}')
