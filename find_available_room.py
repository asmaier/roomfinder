#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import subprocess
import getpass
from string import Template
import xml.etree.ElementTree as ET
import csv, codecs
import argparse
import datetime

now = datetime.datetime.now().replace(microsecond=0)
starttime_default = now.isoformat()
end_time_default = None

parser = argparse.ArgumentParser()
parser.add_argument("-url","--url", help="url for exhange server, e.g. 'https://mail.domain.com/ews/exchange.asmx'.",required=True)
parser.add_argument("-u","--user", help="user name for exchange/outlook",required=True)
parser.add_argument("-start","--starttime", help="Starttime e.g. 2014-07-02T11:00:00 (default = now)", default=starttime_default)
parser.add_argument("-end","--endtime", help="Endtime e.g. 2014-07-02T12:00:00 (default = now+1h)", default=end_time_default)
#parser.add_argument("-n","--now", help="Will set starttime to now and endtime to now+1h", action="store_true")
parser.add_argument("-f","--file", help="csv filename with rooms to check (default=rooms.csv). Format: Name,email",default="rooms.csv")

args=parser.parse_args()

url = args.url

rooms={}
reader = csv.reader(codecs.open(args.file, 'r', encoding='utf-8')) 
for row in reader: 
	rooms[unicode(row[1])]=unicode(row[0])

start_time = args.starttime
if not args.endtime:
	start = datetime.datetime.strptime( start_time, "%Y-%m-%dT%H:%M:%S" )
	end_time = (start + datetime.timedelta(hours=1)).isoformat()
else:
	end_time = args.endtime

user = args.user
password = getpass.getpass("Password:")

print "Searching for a room from " + start_time + " to " + end_time + ":"
print "{0:10s} {1:64s} {2:64s}".format("Status", "Room", "Email")

xml_template = open("getavailibility_template.xml", "r").read()
xml = Template(xml_template)
for room in rooms:
	data = unicode(xml.substitute(email=room,starttime=start_time,endtime=end_time))

	header = "\"content-type: text/xml;charset=utf-8\""
	command = "curl --silent --header " + header +" --data '" + data + "' --ntlm "+"--negotiate "+ "-u "+ user+":"+password+" "+ url
	response = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True).communicate()[0]

	tree = ET.fromstring(response)

	status = "Free"
	# arrgh, namespaces!!
	elems=tree.findall(".//{http://schemas.microsoft.com/exchange/services/2006/types}BusyType")
	for elem in elems:
		status=elem.text

	print "{0:10s} {1:64s} {2:64s}".format(status, rooms[room], room)
