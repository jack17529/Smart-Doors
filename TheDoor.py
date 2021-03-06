# -*- coding: utf-8 -*-

from __future__ import (
    print_function,
)  # to bring the print function from Python 3 into Python 2.6+
import httplib2  # pip2.7.exe install httplib2 --upgrade
import os

# pip2.7.exe install --upgrade google-api-python-client
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import datetime  # for date time functionality.

# =================================================================================================

import urllib2  # to fetch a particular url.
import cv2
import numpy as np
import ssl  # secure socket Layer

# =================================================================================================

import boto3  # for amazon face recognition api (AWS SDK for python)

# =================================================================================================

import csv  # for database.

# =================================================================================================

import smtplib  # for sending emails.

# =================================================================================================

# $ python prog.py -h
# usage: prog.py [-h] [--sum] N [N ...]
# used for the argument parsing in command line.

try:
    import argparse  # to parse the argument and take out flags.

    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = "https://www.googleapis.com/auth/calendar.readonly"
CLIENT_SECRET_FILE = "client_secret.json"
APPLICATION_NAME = "Google Calendar API Python Quickstart"


def get_credentials():
    """Gets valid user credentials from storage.
    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.
    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser(
        "~"
    )  # Windows, return the argument with an initial component of ~
    # or ~user replaced by that user’s home directory
    credential_dir = os.path.join(home_dir, ".credentials")
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(
        credential_dir, "calendar-python-quickstart.json"
    )  # If a component is an absolute path,
    # all previous components are thrown away and joining continues from the
    # absolute path component.

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:  # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print("Storing credentials to " + credential_path)
    return credentials

# =================================================================================================

def main():
    # Make Events here - https://calendar.google.com/calendar/r/day
    """Shows basic usage of the Google Calendar API.
    Creates a Google Calendar API service object and outputs a list of the next
    10 events on the user's calendar.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build("calendar", "v3", http=http)

    now = (
        datetime.datetime.utcnow().isoformat() + "Z"
    )  # 'Z' indicates UTC time // ,timeMax=now
    # datetime.utcnow() uses OS provided values.
    print("Getting the current event")
    eventsResult = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=now,
            maxResults=1,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = eventsResult.get("items", [])  # getting events in an array.

    start = ""  # I will use these in the end while sending mail.
    end = ""
    # summary = ''

    if not events:
        print("No upcoming events found.")
        quit()

    for event in events:
        start = event["start"].get("dateTime", event["start"].get("date"))
        end = event["end"].get("dateTime", event["end"].get("date"))
        # print("start at ->",start,"\n","end at ->",end,"\n", event['summary'])
        
    print("start at ->", start, "\n", "end at ->", end, "\n", event["summary"])
    summary = event["summary"]

    # =============================================================================

    # using IP Webcam.
    # https://docs.python.org/3/library/ssl.html#client-side-operation
    ctx = ssl.create_default_context()  # using at client side.
    ctx.check_hostname = False  # removing check of hostname.
    ctx.verify_mode = ssl.CERT_NONE  # In this mode (the default),
    # no certificates will be required from the other side of the socket connection.
    # If a certificate is received from the other end, no attempt to validate
    # it is made.

    url = "https://192.168.202.3:8080/shot.jpg"

    while True:
        imgResp = urllib2.urlopen(
            url, context=ctx
        )  # this is where the connection is made.
        imgNp = np.array(
            bytearray(imgResp.read()), dtype=np.uint8
        )  # reading image as a numpy array.
        img = cv2.imdecode(imgNp, -1)
        cv2.imshow("test", img)  # showing the image.
        cv2.waitKey(3000)  # waiting for for 3 seconds.
        cv2.imwrite("Unknown.jpg", img)
        break
        # if cv2.waitKey(1000/12) & 0xff ==ord('q'):
        # cv2.imwrite('Unknown.jpg',img)
        # break
        # cv2.waitKey(10)
    cv2.destroyAllWindows()

    # ==============================================================================

    BUCKET_NAME = "trgim"  # target image

    ImageName = "Unknown.jpg"

    data = open(ImageName, "rb")  # opening image as data.
    s3 = boto3.resource("s3")  # using object of s3.
    # putting in bucket.
    s3.Bucket(BUCKET_NAME).put_object(Key=ImageName, Body=data)

    # print ("Done")

    # ================================================================================================

    # s3 = boto3.resource('s3')
    # bucket that contain all the images of the known people.
    BUCKET_NAME2 = "srcim"
    my_bucket = s3.Bucket(BUCKET_NAME2)

    # con2 = 0
    Name = ""

    client = boto3.client(
        "rekognition", "us-east-1"
    )  # Create a low-level service client by name using the default session.
    # service name and region.
    for s3_file in my_bucket.objects.all():
        # print(s3_file.key)
        # con2 = max(con2,Rekon(s3_file.key))        # if similarity is more
        # then 70% then it will be matched.
        if (len(client.compare_faces(SimilarityThreshold=70,
                                     SourceImage={"S3Object": {"Bucket": BUCKET_NAME2,"Name": s3_file.key}},
                                     TargetImage={"S3Object": {"Bucket": BUCKET_NAME,"Name": ImageName}})) != 0):
            response = client.compare_faces(
                SimilarityThreshold=70, 
                SourceImage={"S3Object": {"Bucket": BUCKET_NAME2, "Name": s3_file.key}}, 
                TargetImage={"S3Object": {"Bucket": BUCKET_NAME, "Name": ImageName}})
            for faceMatch in response["FaceMatches"]:
                confidence = str(faceMatch["Face"]["Confidence"])
                if (confidence > 80):  
                    # all images in array that have confidence above 80%.
                    Name = s3_file.key
                    break

    Name = Name[:-4]  # removing extension
    print(Name)

    # ==============================================================================

    email = ""

    with open("data.csv", "r") as f:  # accessing database to find email.
        r = csv.reader(f, delimiter=",")
        for row in r:
            # print(row[0])
            # it has both fiels name and email.
            if len(row) == 2 and row[0] == Name:
                email = row[1]
                # print(email)

    f.close()

    print(email)
    # ============================================================================

    # Removed smtp error - "555 5.5.2 Syntax error. l3sm512374fan.0"
    # https://stackoverflow.com/questions/4421866/cakephp-smtp-emails-syntax-error

    subject = "Did you just tried to Summon The DRAGON ? "

    # print("start at ->",start,"\n","end at ->",end,"\n", event['summary'])

    content = summary + ". Will get time after " + end

    mail = smtplib.SMTP(
        "smtp.gmail.com", 587
    )  # can change the port in the future, the gamil server.
    mail.ehlo()  # for esmtp server.

    mail.starttls()  # TLS support so that login is encrypted.
    # STARTTLS command to convert the connection to a secure TLS channel.

    mail.login(your_email_id, password)

    email_msg = "Subject: {} \n\n{}".format(subject, content)

    mail.sendmail(your_email_id, email, email_msg)
    mail.close()

    # ===============================================================================


if __name__ == "__main__":
    main()
