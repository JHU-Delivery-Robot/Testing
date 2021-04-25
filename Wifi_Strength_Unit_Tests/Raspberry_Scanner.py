from gps3.agps3threaded import AGPS3mechanism
import os
import time
import sys
import json
import subprocess

def getWifi():
    command = 'sudo iw dev wlan0 scan | egrep "^BSS|signal|SSID"'
    while(True):
        try:
            result = subprocess.check_output(command, shell=True)
            break
        except:
            continue

    result = str(result)[2::].replace('(on wlan0)',"")
    result = result.replace('\\n','')
    result = result.replace('\\t','').replace('dBm', '').replace('SSID:','').replace('BSS','').replace('signal:','')

    result = result.split()[:-1]
    tempDict = {}
    wifiList = []
    prevKey = ''
    i = 0

    # MAC Address is key. Value is [dBm,SSId]
    while i < len(result)-2:

        if (result[i].count(':') == 5):
            if tempDict:
                wifiList.append(tempDict)
            tempDict = {}
            tempDict['MAC'] = result[i]
            tempDict['DBM'] = result[i+1]
            tempDict['SSID'] = result[i+2]
            i += 3
        # Handle cases where SSID has spaces
        else:
            tempDict['SSID'] += ' ' + result[i]
            i += 1

    return wifiList


if __name__ == '__main__':

    agps_thread = AGPS3mechanism() # Instantiate AGPS3 Mechanisms
    agps_thread.stream_data() # From localhost (), or other hosts, by example, (host=’gps.ddns .net’)
    agps_thread.run_thread() # Throttle time to sleep after an empty lookup, default ’()’ 0.2 two tenths of a second
    outerDict = {"JsonData":[]}
    i = 0
    while 1:
        temp = agps_thread.data_stream

        data = {}
        data["wifi"] = getWifi()
        data['Latitude'] = temp.lat
        data['Longitude'] = temp.lon
        data['Altitude'] = temp.alt
        print("Iteration : %d %s %s" %(i, data['Latitude'], data['Longitude']))
        i += 1
        outerDict["JsonData"].append(data)
        if (i%100 == 0): # Redundancy - Download current JSON file every 1000 scans
            print("Dumping %s" %(str(i)))
            name = str(i) + '_wifi_gps_data.json'
            with open(name,'w') as outfile:
                json.dump(outerDict, outfile, indent=4)
            print("Written!")

        # i = howevery many iterations we want to walk for
        if (i == 100000):
            print("Dumping %s" % (str(i)))
            name = str(i) + '_wifi_gps_data.json'
            with open(name,'w') as outfile:
                json.dump(outerDict, outfile, indent=4)
            print("Written!")
            print("Exiting!")
            exit(1)

        time.sleep(5) # Adjust this value to our liking