import socket
import json, requests
import sys
import bluetooth
from flask import Flask, render_template, request, redirect, Response
from datetime import datetime
#from pyzbar import pyzbar
#import cv2

serverAddressPort   = ("localhost", 20001)
bufferSize          = 1024
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
URL = "http://127.0.0.1:5000" 

car_id = "VSB296"

def scan():
    print("Scanning...")
    nearby_devices = bluetooth.discover_devices(lookup_names=True)
    print("Found %d devices" % len(nearby_devices))

    for addr, name in nearby_devices:
        devName = name
        add = addr
        print (devName)
        print (add)

def bluelogin():
    print("Scanning...")
    nearby_devices = bluetooth.discover_devices(lookup_names=True)
    resultEmployees = requests.get("{}{}".format(URL, "/employees")) 
    employ = resultEmployees.json() 

    for addr, name in nearby_devices:
        for e in employ:
            if (e['mac_address'] == addr):
                print ("Login successful")
                eng_id = e['username']
                
                #Unlock car
                unlock_str = "_unloCar" + car_id + "_user_" + eng_id
                carRequestBytes = str.encode(unlock_str)
                UDPClientSocket.sendto(carRequestBytes, serverAddressPort)

                print ("Finished maintainenance?")
                print ("y/n")
                while (True):
                    choice = input()
                    if (choice == "y"):
                        
                        #Lock car
                        lock_str = "_lockedCar" + car_id + "_user_" + eng_id
                        lockCarRequestBytes = str.encode(lock_str)
                        UDPClientSocket.sendto(lockCarRequestBytes, serverAddressPort)
                       
                        #Fetch reports
                        reportResult = requests.get("{}{}".format(URL, "/reports"),params={"car_id": car_id, "engineer_id": eng_id})
                        reports = reportResult.json()
                        if (reportResult.status_code == 200):
                            if 'report_id' in reports:
                                print (reports)
                                print ("please select report to complete")     
                                choice = input()
                                #Update report
                                now = datetime.now()
                                dt = now.strftime("%Y-%m-%d %H:%M:%S")
                                resultPutReport = requests.put("{}{}".format(URL, "/report"),params={"report_id": choice, "engineer_id": eng_id, "complete_date":dt})
                                if (resultPutReport.status_code == 200):
                                    print ("car report updated")
                                else:
                                    print ("car report failed to update")    
                            else: 
                                print ("no reports found car locked")
                        else:
                            print ("failed to fetch reports car locked")
                        return True

                    elif (choice == "n"):
                        #Lock car
                        lock_str = "_lockedCar" + car_id + "_user_" + eng_id
                        lockCarRequestBytes = str.encode(lock_str)
                        UDPClientSocket.sendto(lockCarRequestBytes, serverAddressPort)
                        return True
                    else:
                        print ("invalid choice")
    return False
"""
def qrlogin():
    image = cv2.imread("jwoodroffe.png")
    mask = cv2.inRange(image,(0,0,0),(200,200,200))
    thresholded = cv2.cvtColor(mask,cv2.COLOR_GRAY2BGR)
    inverted = 255-thresholded # black-in-white
    barcodes = pyzbar.decode(inverted)
    foundData = ""
    for barcode in barcodes:
        barcodeData = barcode.data.decode("utf-8")
        barcodeType = barcode.type
        if barcodeType == "QRCODE":
            if barcodeData is not foundData:
                username = barcodeData
                #if username exists in db login
                #print ("Login successful car locked")
                #unlock car
                #print ("Finished maintainenance?")
                #print ("y/n")
                #lock car
                #update maintenance table
            else:
                print("QR Code doesn't have data")
        else:
            print("Data is not a QR code")
"""
def interface():
    if (bluelogin() != True):
        while (True):   
            options = {
                "1: Login with QR code": "",
                "2: Scan login with bluetooth again":"",
                "3: Scan for nearby bluetooth devices":""
                }
            for x in options: 
                print (x)
            print ("Select an option...")
            selectedOption = input()
            #if (selectedOption == "1"):
                #qrlogin()          
            if (selectedOption == "2"):
                bluelogin()
            elif (selectedOption == "3"):
                scan()
            else:
                print("invalid choice")
           
if __name__ == "__main__":
   interface()
    
 
    
    