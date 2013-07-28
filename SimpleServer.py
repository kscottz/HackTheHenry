#!/usr/bin/python
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from os import curdir, sep
import cgi
import soundcloud
from twilio.rest import TwilioRestClient
import xml.etree.ElementTree as ET
import urllib
import subprocess
import os
import pickle
import SimpleCV as scv
import time
import twitter
import base64
import json
import requests
import string 
from base64 import b64encode

PORT_NUMBER = 8080
#This class will handles any incoming request from
#the browser 
class myHandler(BaseHTTPRequestHandler):
    #Handler for the GET requests
    def tweetDat(self,msg):
        pkl_file = open('sc.pkl', 'rb')
        sc = pickle.load(pkl_file)
         
        twit = twitter.Api(sc['twitID'],sc['twitSecret'],sc['accessToken'],sc['accessSecret'])
        # Now work with Twitter
        print msg
        twit.PostUpdate(msg)

    def do_GET(self):
        if self.path=="/":
            self.path="/index.html"#exhibit-items-screen.html"
        try:
            #Check the file extension required and
            #set the right mime type
            
            sendReply = False
            if self.path.endswith(".html"):
                mimetype='text/html'
                sendReply = True
            if self.path.endswith(".jpg"):
                mimetype='image/jpg'
                sendReply = True
            if self.path.endswith(".gif"):
                mimetype='image/gif'
                sendReply = True
            if self.path.endswith(".js"):
                mimetype='application/javascript'
                sendReply = True
            if self.path.endswith(".css"):
                mimetype='text/css'
                sendReply = True

            if sendReply == True:
                #Open the static file requested and send it
                f = open(curdir + sep + self.path) 
                self.send_response(200)
                self.send_header('Content-type',mimetype)
                self.end_headers()
                self.wfile.write(f.read())
                f.close()
            return
        
        except IOError:
            self.send_error(404,'File Not Found: %s' % self.path)

    #Handler for the POST requests
    def do_POST(self):
        self.exhibitList = ['00.136.123','19.3.1','00.241.1','81.9.1','87.154.1','48.6.1','2011.329.2','2011.329.1','2011.392.1']

        self.objMap = {
            '00.136.123': (625, 440),
            '19.3.1': (625,425),
            '00.241.1': (630,410),
            '81.9.1': (645,380),
            '87.154.1': (650,360),
            '48.6.1': (660,310),
            '2011.329.2': (675,195),
            '2011.329.1': (690,200),
            '2011.392.1': (685,171)
            }

        if self.path=="/send":
            form = cgi.FieldStorage( fp=self.rfile, 
                                     headers=self.headers,
                                     environ={'REQUEST_METHOD':'POST',
                                              'CONTENT_TYPE':self.headers['Content-Type'],})
            print form
            data = []
            cdata = {}
            for f in form:
                if( f[0:4] == 'item' ):
                    data.append(form[f].value)
                if( f == 'twitter'):
                    cdata['twitter'] = form[f].value
                if( f == 'textmsg'):
                    cdata['phone']= form[f].value
                if( f == 'email'):
                    cdata['email'] = form[f].value
                print form[f].value
            print cdata
            #self.send_response(200)
            #self.end_headers()
            
            #self.wfile.write(open('thanks.html','r'))
            #Open the static file requested and send it
            f = open(curdir + sep + 'thanks.html') 
            mimetype='text/html'
            self.send_response(200)
            self.send_header('Content-type',mimetype)
            self.end_headers()
            self.wfile.write(f.read())
            f.close()

            #comment this out
            #result = self.buildTour(data)
            snd = self.SendToSC("out.mp3")
            link = self.uploadImgur('magic2.gif')#outMap.png')
            if( cdata.has_key('phone') ):
                msg = "Henry Ford map: {0} & audio {1}".format(link,snd)
                pn = cdata['phone']
                all=string.maketrans('','')
                nodigs=all.translate(all, string.digits)
                pn = pn.translate(all, nodigs)
                pn = "+1"+pn
                self.sendSMS(msg,pn)
                
            if( cdata.has_key('twitter') ):
                #link = self.uploadImgur('magic2.gif')
                msg = ".{0} here is your Henry Ford #HackTheMuseum Audio tour: {1} and map {2}".format(cdata['twitter'],snd,link)
                self.tweetDat(msg)

        return

    def sendSMS(self,msg,toNumber,fromNumber='+17347961119'):
        pkl_file = open('sc.pkl', 'rb')
        sc = pickle.load(pkl_file)
        account_sid = sc["twilioID"]
        auth_token = sc["twilioSecret"]
        client = TwilioRestClient(account_sid, auth_token)        
        message = client.sms.messages.create(to=toNumber, from_=fromNumber,body=msg)
        print message
			
    def uploadImgur(self,fname,name="Map!",title="Your Map of the Henry Ford"):
        pkl_file = open('sc.pkl', 'rb')
        sc = pickle.load(pkl_file)
        headers = {"Authorization": "Client-ID {0}".format(sc['imgurID'])}
        api_key = sc['imgurID']
        url = "https://api.imgur.com/3/upload.json"
        j1 = requests.post(
            url, 
            headers = headers,
            data = {
                'key': api_key, 
                'image': b64encode(open(fname, 'rb').read()),
                'type': 'base64',
                'name': name,
                'title': title
                }
            )

        data = json.loads(j1.text)['data']
        print data
        return data['link']

            
    def getObjData(self,id='83.190.1'):    
        itemstr = 'http://api.makerfairedetroit.com/item.aspx?objectid={0}'.format(id)
        stuff = urllib.urlretrieve(itemstr)
        tree = ET.parse(stuff[0])
        root = tree.getroot()
        retVal = {}
        pics = root.findall('.//resource')
        imgs = []
        for d in pics:
            for k,v in d.attrib.iteritems():
                if k == 'thumbnailFile':
                    imgs.append(scv.Image(v))
                    break
        for child in root:
            for k,v in child.attrib.iteritems():
                retVal[k] = v
        retVal['thumbs'] = imgs
        return retVal

    def textToWav(self,text,file_name):
        print "txt to wav"
        subprocess.call(["espeak","-ven-us","-s120","-a150","-p80","-w"+file_name,text])
    # 
    def wavToMp3(self,infile='temp.wav',outfile='temp.mp3'):
        print "wav to mp3"
        os.system('lame -s22.05k -b16k {0} {1}'.format( infile, outfile))

    def generateTour(self,exhibitList):
        startStr = "\n\n\n You should now be at exhibit {0} located at {1}{2}. \n\n\n"
        endStr = "\n\n\n Please pause the audio and proceed to exhibit {0} located at {1}{2}.\n\n\n"
        exhibitData = []
        for exhibit in exhibitList:
            exhibitData.append(self.getObjData(id=exhibit))

        finalStr = "Welcome to your virtual tour at the Henry Ford Museum. "
        count = 0 
        for exhibit in exhibitData:
            if count > 0:
                finalStr += endStr.format(exhibit['title'],exhibit['CurrLocation2'],exhibit['CurrLocation3'])     
            count = count + 1
            finalStr += startStr.format(exhibit['title'],exhibit['CurrLocation2'],exhibit['CurrLocation3'])   
            finalStr += exhibit['abstract']
            if( exhibit.has_key('abstractExp') ):
                finalStr += exhibit['expAbstract'] 
        finalStr+="\n\n\n This concludes our tour. Thank you for visiting the Henry Ford Museum."
        print finalStr
        return finalStr,exhibitData

    def SendToSC(self,filename,title="Autogenerated"):
        pkl_file = open('sc.pkl', 'rb')
        sc = pickle.load(pkl_file)
        client = soundcloud.Client(client_id=sc['sc_id'],
                                   client_secret=sc['sc_secret'],
                                   username = sc['sc_un'],
                                   password = sc['sc_pw'])

        track = client.post('/tracks', track={
            'title': title,
            'sharing': 'public',  # make this 'public' if you want
            'asset_data': open(filename, 'rb')
            })
        print track.permalink_url
        return track.permalink_url

    def buildMap(self,mapImg,exhibitList,data,objMap):
        last = objMap[exhibitList[0]]
        mapImg.drawText('START',last[0],last[1])
        #derp = scv.ImageSet()
        for exhibit,info in zip(exhibitList,data):
            curr = objMap[exhibit]
            thumb = info['thumbs'][0].scale(0.5)
            offset = (thumb.width/2,thumb.height/2)
            mapImg = mapImg.applyLayers()
            mapImg = mapImg.blit(thumb,(curr[0]-offset[0],curr[1]-offset[1]),mask=thumb.binarize())
            mapImg.drawText(info['title'],curr[0]+20,curr[1]-20)
            mapImg.drawLine(last,curr,thickness=1,color=scv.Color.RED)
            mapImg.drawCircle(curr,4,color=scv.Color.RED,thickness=3)
            last = curr
            mapImg = mapImg.applyLayers()
            #derp.append(mapImg)
        #derp.save('magic.gif')
        retVal = mapImg.applyLayers()
        return retVal

    def buildTour(self,exhibitList):
        mapImg = scv.Image('./images/map.png')
        myStr,data = self.generateTour(exhibitList)
        self.textToWav(myStr,'out.wav')
        self.wavToMp3('out.wav','out.mp3')
        out = self.buildMap(mapImg,exhibitList,data,self.objMap)
        out.save('outMap.png')
        result = self.SendToSC('out.mp3',"HELLO WORLD!!!")
        return result

    
try:
    server = HTTPServer(('', PORT_NUMBER), myHandler)
    print 'Started httpserver on port ' , PORT_NUMBER	
    #Wait forever for incoming htto requests
    server.serve_forever()

except KeyboardInterrupt:
    print '^C received, shutting down the web server'
    server.socket.close()
