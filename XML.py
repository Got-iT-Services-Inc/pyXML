#! /usr/bin/env python3
#############################################################
# Title: Python XML Data Class                              #
# Description: Handles XML text structure and allows the    #
#              easy access to the raw data                  #
# Version:                                                  #
#   * Version 1.0 10/22/2015 RC                             #
#                                                           #
# Author: Richard Cintorino (c) Richard Cintorino 2015      #
#############################################################

import base64
import sys
import inspect, os
sCurPath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) # script directory

from Debug import pyDebugger

class pyXMLTag():

    def __eq__(self,other):
        if isinstance(other, self.__class__):
           return self.__dict__ == other.__dict__
        else:
            return False

    #Initialize our class and chop data
    def __init__(self, sXMLData, sKey, bDebug=True, bEncryption = True):
        self.Debugger = pyDebugger(self,bDebug,False)
        self.Debugger.Log("Initializing XML Data Class with Encryption=" + str(bEncryption) + "...")
        
        self.__sData = ""
        self.__dKeys = {}
        self._bDataEncryption = True
        self.isValid = False
       
        #Set Encryption
        self._bDataEncryption = bEncryption
        #check for valid key
        if sKey == "":
            self.isValid = False
            self.Debugger.Log("*************************************************")
            self.Debugger.Log("PXML Error: No Key Provided")
            self.Debugger.Log("*************************************************")
            return
        else:
            #set start and stop keys
            sKeyStart = "<" + sKey 
            self.Debugger.Log("KeyStart set to '" + sKeyStart + "'")
            sKeyStop = "</" + sKey + ">"
            self.Debugger.Log("KeyStop set to '" + sKeyStop + "'")
            #try and get the position of the start key
            try:
                iKeyStart = sXMLData.index(sKeyStart) + len(sKeyStart)
                self.Debugger.Log("KeyStart index is '" + str(iKeyStart) + "'")
            except:
                self.Debugger.Log("*************************************************")
                self.Debugger.Log("PXML Error: Couldn't find StartKey in XML Data!")
                self.Debugger.Log("XML='" + str(sXMLData) + "'")
                self.Debugger.Log("*************************************************")
                return
            #try and get the position of the end key
            iKeyStop = sXMLData.find(sKeyStop) 
            if iKeyStop > -1:    
                self.Debugger.Log("KeyStop index is '" + str(iKeyStop) + "'")
            else:
                self.Debugger.Log("PXML Warning: Couldn't find StopKey in XML Data!")
            #Try and find our start tag end
            try:
                iKeyStartStop = sXMLData.find(">",iKeyStart)
                self.Debugger.Log("KeyStartStop index is '" + str(iKeyStartStop) + "'")
            except:
                self.Debugger.Log("***************************************************")
                self.Debugger.Log("PXML Error: Couldn't find KeyStartStop in XML Data!")
                self.Debugger.Log("XML='" + sXMLData + "'")
                self.Debugger.Log("***************************************************")
                return

                
            #check to make sure our range is valid
            if iKeyStop - iKeyStart > 0:
                #Get our data and store it
                self.Set_Data(sXMLData[(iKeyStartStop+1):iKeyStop])
                self.isValid = True
                self.Debugger.Log("Valid Data Found...")
            
            #Check to see if w have data in our start tag
            if iKeyStartStop - iKeyStart > 2:
                self.Debugger.Log("Extracting Additional Key Data...")
                #We have data within the start tag, parse it out
                sKeystring = sXMLData[(iKeyStart+1):iKeyStartStop]
                #if self.__Debug == True:
                #    print("Data is: " + sKeystring + "\nLength is: " + str(len(sKeystring)))
                sTmp = ""
                bKy = True
                bFoundQ = False
                sKy = ""
                sVl = ""
                bLoop = 0
                for bLoop in range(len(sKeystring)):
                    #print("Char index is '" + str(bLoop) + "' Char is '" + sKeystring[bLoop:(bLoop+1)] + "'")
                    if sKeystring[bLoop:(bLoop+1)] == " ":
                        #we got a space, so check if our variables are full or empty
                        #print("Key '" + sKy + "' Value is '" + sVl + "'")
                        if sKy != "" and sVl != "" and bFoundQ == False:
                        #our variables are full, so save them as key value pair
                            self.Debugger.Log("Saving Key '" + sKy + "' Value is '" + sVl + "'")
                            self.Set_Key(self,sKey.replace('"',""),sVl.replace('"',""))
                            sKy = ""
                            sVl = ""
                            bKy = True
                            self.isValid = True
                        else:
                            if bFoundQ == True and bKy == False:
                                #this is still part of a value
                                sVl = sVl + sKeystring[bLoop:(bLoop+1)]
                            else:
                                #there should be no spaces before key and value is filled!
                                #so error here, reset variables
                                sKy = ""
                                sVl = ""
                    elif sKeystring[bLoop:(bLoop+1)] == "=":
                        #we need to switch to value vars
                        #self.Debugger.Log("Key is '" + sKy + "'. Switching from Key to Value...")
                        bKy = False
                    elif sKeystring[bLoop:(bLoop+1)] == '"':
                        #we only care if we're already found an '='
                        if bKy == False:
                            if bFoundQ == True:
                                self.Set_Key(sKy,sVl)
                                sKy = ""
                                sVl = ""
                                bFoundQ = False
                                bKy = True
                            else:
                                bFoundQ = True
                    else:
                        if bKy == True:
                            sKy = sKy + sKeystring[bLoop:(bLoop+1)]
                        else:
                            sVl = sVl + sKeystring[bLoop:(bLoop+1)]
                self.isValid = True
            else:
                self.Debugger.Log("Key Data Not Found...")
            self.Debugger.Log("*************************************************")
            
    def __ne__(self,other):
        return not self.__eq__(other)
    
    #Excludes a specific key tag and everything between it.
    def _Exclude(self, sKey):
        sTemp = ""
        sKeyStart = ""
        sKeyStop = ""
        iKeyStart = -1
        iKeyStop = -1
        bKeepGoing = True        

        try:
            sKeyStart = "<" + sKey
            sKeyStop = "</" + sKey + ">"

            while bKeepGoing:
                iKeyStart = self.__sData.find(sKeyStart)
                iKeyStop = self.__sData.find(sKeyStop)
                if iKeyStart > -1:
                    if iKeyStop < 0:
                        #We don't have an end tag, so search for the >!
                        sTD = self.__sData[iKeyStart:]
                        for aLoop in range(len(sTD)):
                            if sTD[aLoop:(aLoop+1)] == ">":
                                iKeyStop = aLoop+2
                                bKeepGoing = False
                                break
                    if iKeyStop > -1:
                        self.Debugger.Log("iKeystop=" + str(iKeyStop) + " and sKeyStop="+sKeyStop)  
                        sTemp = self.__sData[0:(iKeyStart -1)]
                        self.__sData = sTemp + self.__sData[iKeyStop+(len(sKeyStop)+1):len(self.__sData)]
                        self.Debugger.Log("Data after exclusion: \n\n" + self.__sData)
                    else:
                        bKeepGoing = False
                else:
                    bKeepGoing = False 
                            
            else:
                self.Debugger.Log("Can't find KeyStart for exclusion: \n\n" + self.__sData)

        except Exception as e:
            self.Debugger.Log("PXML::_Exclude Error: " + str(e))
        return sTemp 

    def Get_Data(self):
        return self.__sData

     #Gets a value from our dict with a key
    def Get_Key(self,sKey):
        #print (self.__dKeys.items())
        try:
            #Can we return the value?
            if sKey in self.__dKeys:
                return self.__dKeys[sKey]
            else:
                return "-1"
        #If they key doesn't exist we error
        except Exception as e:
            self.Debugger.Log("PXML::Get_Key Error: " + str(e))
            return ""
    
    #Update a value in our dictionary
    def Update_Key(self,sKey,sValue):
        if sKey in self.__dKeys:
            self.Debugger.Log("Updating key '" + sKey + "' with value '" + sValue + "'...",endd='')
        else:
            self.Debugger.Log("Adding key '" + sKey + "' with value '" + sValue + "'...",endd='')
        self.__dKeys[sKey] = sValue

    #Remove a value from our dictionary
    def Remove_Key(self,sKey):
        self.Debugger.Log("Removing Key '" + sKey +"'...",endd='')
        if sKey in self.__dKeys:
            self.__dKeys.pop(sKey,None)
            self.Debugger.Log("Success!")
            return True
        else:
            self.Debugger.Log("Failed! Key doesn't exist")
            return False
                
    def Set_Data(self, value):
        if self._bDataEncryption == True:
            self.Debugger.Log("Base64 Ecryption Off...")
            self.__sData = base64.b64decode(value)
        else:
            self.Debugger.Log("Base64 Ecryption Off...")
            self.__sData = value
        self.Debugger.Log("Setting Data to: \n" + value)
                                
    #Set our key/value pair in our dict if it doesn't exist already
    def Set_Key(self,sKey,sValue):
        bSaveValue = True
        #check if the key exists
        #print (self.__dKeys.items())
        if sKey not in self.__dKeys:
            self.Debugger.Log("Saving Key '" + sKey + "', Value is '" + sValue + "'")
            self.__dKeys[sKey] = sValue
        else:
            self.Debugger.Log("Key  '" + sKey + "' Exists with Value '" + self.__dKeys[sKey] + "'") 
            bSaveValue = False
        return bSaveValue

    Data = property(Get_Data,Set_Data)
    
            
            