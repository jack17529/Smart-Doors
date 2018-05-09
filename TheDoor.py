# -*- coding: utf-8 -*-
from __future__ import print_function
import httplib2                         #pip2.7.exe install httplib2 --upgrade
import os

from apiclient import discovery         #pip2.7.exe install --upgrade google-api-python-client
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import datetime
#=================================================================================================

import urllib2
import cv2
import numpy as np
import ssl

#=================================================================================================

import boto3
from botocore.client import Config

#=================================================================================================

import csv

#=================================================================================================

import smtplib

#=================================================================================================

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'

def get_credentials():
    """Gets valid user credentials from storage.
    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.
    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

#=================================================================================================
'''
#Removed because of the s3 meta data error.
def Rekon(src,s):
    s3 = s
    bucket = 'srcim'
    sourceFile=src    #source.jpg
    targetFile='Unknown.jpg'             #target.jpg

    client=boto3.client('rekognition','us-east-1')

    response=client.compare_faces(SimilarityThreshold=70,
                                  SourceImage={'S3Object':{'Bucket':bucket,'Name':sourceFile}},
                                  TargetImage={'S3Object':{'Bucket':bucket,'Name':targetFile}})

    if len(response['FaceMatches'])==0:
        return 0
    else:
        for faceMatch in response['FaceMatches']:
            position = faceMatch['Face']['BoundingBox']
            confidence = str(faceMatch['Face']['Confidence'])
            if(con>80):
                return confidence
            #print('The face at ' +
                   #str(position['Left']) + ' ' +
                   #str(position['Top']) +
                   #' matches with ' + confidence + '% confidence')
    #return con 
'''
#=================================================================================================

def main():
    #Make Events here - https://calendar.google.com/calendar/r/day
    """Shows basic usage of the Google Calendar API.
    Creates a Google Calendar API service object and outputs a list of the next
    10 events on the user's calendar.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time // ,timeMax=now
    print('Getting the current event')
    eventsResult = service.events().list(
        calendarId='primary', timeMin=now, maxResults=1, singleEvents=True,
        orderBy='startTime').execute()
    events = eventsResult.get('items', [])

    start = ''
    end = ''
    #summary = ''

    if not events:
        print('No upcoming events found.')
        quit()

    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime',event['end'].get('date'))
        #print("start at ->",start,"\n","end at ->",end,"\n", event['summary'])

    print("start at ->",start,"\n","end at ->",end,"\n", event['summary'])

    summary = event['summary']

    #=================================================================================================
    
    #using IP Webcam.

    ctx = ssl.create_default_context()             
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    url = 'https://192.168.201.2:8080/shot.jpg'

    while True:
        imgResp = urllib2.urlopen(url,context=ctx)
        imgNp = np.array(bytearray(imgResp.read()),dtype=np.uint8)
        img = cv2.imdecode(imgNp,-1)
        cv2.imshow('test',img)
        cv2.waitKey(3000)
        cv2.imwrite('Unknown.jpg',img)
        break
        #if cv2.waitKey(1000/12) & 0xff ==ord('q'):
            #cv2.imwrite('Unknown.jpg',img)
            #break
        #cv2.waitKey(10)
    cv2.destroyAllWindows()
    
    #==================================================================================================

    #ACCESS_KEY_ID = 'AKIAJRBXB5I4DBCIZNFA'
    #ACCESS_SECRET_KEY = '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'
    BUCKET_NAME = 'trgim' #target image

    ImageName = 'Unknown.jpg'

    data = open(ImageName , 'rb')
    '''
    #Removed because unsafe. 
    s3 = boto3.resource(
        's3',
        aws_access_key_id=ACCESS_KEY_ID,
        aws_secret_access_key=ACCESS_SECRET_KEY,
        config=Config(signature_version='s3v4')
    )
    '''
    s3 = boto3.resource('s3')
    s3.Bucket(BUCKET_NAME).put_object(Key=ImageName, Body=data)

    #print ("Done")

    #================================================================================================

    #s3 = boto3.resource('s3')
    BUCKET_NAME2 = 'srcim'
    my_bucket = s3.Bucket(BUCKET_NAME2)

    #con2 = 0
    Name = ''

    client=boto3.client('rekognition','us-east-1')

    for s3_file in my_bucket.objects.all():
        #print(s3_file.key)
        #con2 = max(con2,Rekon(s3_file.key))
        if (len(client.compare_faces(SimilarityThreshold=70,
                                  SourceImage={'S3Object':{'Bucket':BUCKET_NAME2,'Name':s3_file.key}},
                                  TargetImage={'S3Object':{'Bucket':BUCKET_NAME,'Name':ImageName}}))!=0):
            response = (client.compare_faces(SimilarityThreshold=70,
                                  SourceImage={'S3Object':{'Bucket':BUCKET_NAME2,'Name':s3_file.key}},
                                  TargetImage={'S3Object':{'Bucket':BUCKET_NAME,'Name':ImageName}}))
            for faceMatch in response['FaceMatches']:
                position = faceMatch['Face']['BoundingBox']
                confidence = str(faceMatch['Face']['Confidence'])
                if(confidence>80):
                    Name = s3_file.key
                    break
            

    Name = Name[:-4]
    print (Name)
    
    #================================================================================================

    email=''

    with open('data.csv','r') as f:
        r=csv.reader(f,delimiter=',')
        for row in r:
            #print(row[0])
            if len(row)==2 and row[0]==Name:
                email = row[1]
                #print(email)

    f.close()

    print(email)
    #================================================================================================

    #Removed smtp error - "555 5.5.2 Syntax error. l3sm512374fan.0"
    #https://stackoverflow.com/questions/4421866/cakephp-smtp-emails-syntax-error

    subject = 'Did you just tried to Summon The DRAGON ? '

    #print("start at ->",start,"\n","end at ->",end,"\n", event['summary'])

    content = summary+'. Will get time after '+ end

    mail = smtplib.SMTP('smtp.gmail.com',587)   #can change the port in the future
    mail.ehlo()                                 #for esmtp server.

    mail.starttls()                             #TLS support so that login is encrypted.

    mail.login('jackcoreman1729@gmail.com','Rama@171969')

    email_msg = "Subject: {} \n\n{}".format(subject,content)

    mail.sendmail('jackcoreman1729@gmail.com',email,email_msg)
    mail.close()
    
    #===============================================================================================

if __name__ == '__main__':
    main()
 