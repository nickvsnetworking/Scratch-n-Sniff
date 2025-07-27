import logging
logging.basicConfig(level=logging.DEBUG)
import shutil
import glob
import time
import gzip
import os
import socket
import yaml
from pathlib import Path

# Local Capture agent for cylic packet capturing.
# Parameters such as maximum number of pcap files kept, source port and rotation size are defined in config.yaml

with open("config.yaml", 'r') as configFile:
    yamlConfig = (yaml.safe_load(configFile))

maxFilesize = yamlConfig.get("localCapture", {}).get("maxFilesize", "200000") # Default 200mb max file size
maxPcaps = yamlConfig.get("localCapture", {}).get("maxPcaps", "5") # Default max 5 pcaps
outputFile = yamlConfig.get("localCapture", {}).get("outputFile", "/etc/localcapture/localCapture.pcap") # Default to the local directory
outputDirectory = str(Path(outputFile).parent)
portList = yamlConfig.get("localCapture", {}).get("portList", [])
enableCompression = yamlConfig.get("localCapture", {}).get("enableCompression", True)
hostname = socket.gethostname()

#Include a port filter, if defined.
portFilter = ""
if portList:
    portFilter = ' or '.join(f'port {port}' for port in portList)
    portFilter = '-f ' + '"' + portFilter + '"'

def rotatingCapture():
    while True:
        # Check if the output directory contains more pcaps than maxPcaps. If it does, keep only the newest maxPcaps (eg 20).
        files = sorted(glob.glob(f'{outputDirectory}/*.pcap.gz'), key=os.path.getmtime)
        print(files)
        oldPcaps = files[:-maxPcaps] if len(files) > maxPcaps else []
        for file in oldPcaps:
            print(f"Removing {file}")
            os.remove(file)

        # Capture the PCAP
        print(f"Running: dumpcap -i any -w {outputFile} -a filesize:{maxFilesize} {portFilter}")
        os.system(f'dumpcap -i any -w {outputFile} -a filesize:{maxFilesize} {portFilter}')
        print("Done")

        timestamp = time.strftime("%Y%m%d-%H%M%S")
        # Give the PCAP a unique name by appending the timestamp
        finalFilename = f'{hostname}_{timestamp}.pcap'
        os.rename(outputFile, finalFilename)

        if enableCompression:
            # Compress the file using GZIP, then delete the uncompressed file
            with open(finalFilename, 'rb') as f_in, gzip.open(f'/{outputDirectory}/{finalFilename}' + '.gz', 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
            os.remove(finalFilename)
        
        # Remove any stray .pcap files, incase they exist.
        try:
            os.system(f'rm {outputDirectory}/*.pcap')
        except Exception as e:
            pass

        # Set '777' Permissions on the PCAP folder contents
        os.system((f'chmod -R 777 {outputDirectory}'))


if __name__ == '__main__':
    rotatingCapture()
