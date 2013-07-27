import xml.etree.ElementTree as ET
import urllib


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

stuff = getObjData()
print 30*'$'
for key, value in stuff.iteritems():
    print "{0}-->{1}".format(key,value)
