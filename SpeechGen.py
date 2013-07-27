import xml.etree.ElementTree as ET
import urllib
import subprocess
import os

def getObjData(id='83.190.1'):    
    itemstr = 'http://api.makerfairedetroit.com/item.aspx?objectid={0}'.format(id)
    stuff = urllib.urlretrieve(itemstr)
    tree = ET.parse(stuff[0])
    root = tree.getroot()
    retVal = {}
    for child in root:
        for k,v in child.attrib.iteritems():
            retVal[k] = v
    return retVal

def textToWav(text,file_name):
   subprocess.call(["espeak", "-s90","-a150", "-w"+file_name,text])

def wavToMp3(infile='temp.wav',outfile='temp.mp3'):
    os.system('lame -s22.05k -b16k {0} {1}'.format( infile, outfile))


stuff = getObjData()

textToWav(stuff['abstract'],'temp.wav')
wavToMp3()

# print 30*'$'
# for key, value in stuff.iteritems():
#     print "{0}-->{1}".format(key,value)



# import pyttsx
# engine = pyttsx.init()
# engine.setProperty('rate',120)
# engine.setProperty('volume',1)
# engine.say(stuff['abstract'])
# engine.runAndWait()
