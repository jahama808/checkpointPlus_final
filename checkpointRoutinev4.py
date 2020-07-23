#!/usr/bin/python

# Code Version #
software = "7/22/2020"

import pandas as pd
import os,subprocess
from pandas.io.json import json_normalize
import numpy as np
from serial import Serial
import time,MySQLdb
from settings import *
from target2 import *
import datetime


class SpeedTest:

	def __init__(self,df):
		"""This is the thing that holds all the speedtest results"""
		self.target =df[df['download']==df['download'].max()]['server'].iloc[0] 
		self.down = int(df[df['download']==df['download'].max()]['download'].iloc[0]/1000000)
		self.up = int(df[df['download']==df['download'].max()]['upload'].iloc[0]/1000000)
		self.latency = int(df[df['download']==df['download'].max()]['latency'].iloc[0])
		self.sponsor = df[df['download']==df['download'].max()]['sponsor'].iloc[0]
		self.share = df[df['download']==df['download'].max()]['share'].iloc[0]	


def main():

	#create unitID from mac address

	direct_output = subprocess.check_output('ifconfig eth0 | grep ether', shell=True)
	unitID = "HT:{}".format(direct_output[direct_output.find('ether',0)+15:direct_output.find('  txqueuelen')])
	print("unit ID: {}".format(unitID))

	print("DEBUG:Execution begin at ",datetime.datetime.now())

	while True:
		#use this for Raspberry Pi's
		port=Serial(port='/dev/ttyAMA0',baudrate=9600, timeout=1.0)


		eof = "\xff\xff\xff"
		Page = 0 #page0 is the norm and page 1 is all black with large #'s for easy reading in the AM

		#show the intro screen
		port.write("page 5" + eof)



		#switch to page 4 - show unitID
		port.write("page 4"+eof)
		port.write('page4.deviceID.txt="'+str(unitID)+'"'+eof)
		port.write('page4.softwareID.txt="'+software+'"'+eof)
		time.sleep(5)


		#create the results dataframe

		results_df= pd.DataFrame(columns = ['server','test-type','download','upload','latency','sponsor','share'])


		#Get WAN IP

		direct_output = subprocess.check_output('curl ifconfig.me', shell=True)
		print ("WAN IP: {}").format(direct_output)
		wanIP = direct_output

		# Get LAN IP
		direct_output = subprocess.check_output('ip address show eth0 | grep inet | grep eth0', shell=True)
		print ("LAN IP: {}").format(direct_output[direct_output.find("inet",1)+5:direct_output.find("brd",1)-1])
		lanIP = direct_output[direct_output.find("inet",1)+5:direct_output.find("brd",1)-1]
		justLanIP =  lanIP[:lanIP.find("/",1)]
		lanIP = justLanIP


		print("DEBUG: Starting Multi-thread Ookla tests")

		port.write("page 1"+eof)
		showserver="HT"

		for target in ooklaTargets:

			port.write("page 1"+eof)
			port.write('page1.target.txt="'+str(showserver)+'"'+eof)
			print("DEBUG: 	Target server {} starting".format(target))
			try:
				result = subprocess.check_output("/home/pi/speedtest-cli --json  --mini http://{}".format(target), shell=True)
			
				df = pd.read_json(result)
				results_df = results_df.append({'server':target,'test_type':'multi-thread','download':df['download'].iloc[0],'upload':df['upload'].iloc[0],'latency':df['ping'].iloc[0],'sponsor':df['server'].iloc[df.index.get_loc('sponsor')],'share':df['share'].iloc[0]},ignore_index=True)
				print("DEBUG: 	Target server {} completed".format(target))
			except:
				print("DEBUG: Failed to contact server")

		print("DEBUG: Multi-thread ookla tests completed")
		print("DEBUG: Starting Single-thread Ookla tests")
		port.write("page 2"+eof)

		for target in ooklaTargets:

				port.write("page 2"+eof)
				port.write('page2.target.txt="'+str(showserver)+'"'+eof)

				print("DEBUG: 	Target server {} starting".format(target))
				try:
					result = subprocess.check_output("/home/pi/speedtest-cli --json  --single --mini http://{}".format(target), shell=True)
					df = pd.read_json(result)
					results_df = results_df.append({'server':target,'test_type':'single-thread','download':df['download'].iloc[0],'upload':df['upload'].iloc[0],'latency':df['ping'].iloc[0],'sponsor':df['server'].iloc[df.index.get_loc('sponsor')],'share':df['share'].iloc[0]},ignore_index=True)
					print("DEBUG: 	Target server {} completed".format(target))	
				except:
					print("DEBUG: Failed to contact server")

		print("DEBUG: Single-thread ookla tests completed")


		# create new dataframes for the multithreaded results and single threaded results

		try:
			st_df = results_df[results_df['test_type']=='single-thread']
			singlethread = SpeedTest(st_df)
		except:
			print("DEBUG: Failed to extract single threaded results <----------------------")

		try:
			mt_df = results_df[results_df['test_type']=='multi-thread']
			multithread = SpeedTest(mt_df)
		except:
			print("DEBUG: Failed to extract multi threaded results <---------------------")

		
		# Open up the database  connection
		conn = MySQLdb.connect(host=host,port=dbport,user=dbUser,passwd=dbPass,db=database)
		c = conn.cursor()
		
		try:
			result = "insert into panda_results (identity,wanip,lanip,multithread_down,multithread_up,multithread_target,multithread_latency,multithread_sponsor,multithread_share,\
		singlethread_down,singlethread_up,singlethread_target,singlethread_latency,singlethread_sponsor,singlethread_share,timeCreated)\
		values (\"{}\",\"{}\",\"{}\",{},{},{},{},\"{}\",\"{}\",{},{},{},{},\"{}\",\"{}\",\"{}\");".\
		format(unitID,wanIP,lanIP,multithread.down,multithread.up,34623,multithread.latency,"Hawaiian Telcom",multithread.share,\
		singlethread.down,singlethread.up,34623,singlethread.latency,"Hawaiian Telcom",singlethread.share,datetime.datetime.now())
			print("DEBUG: Pushed to database at ",datetime.datetime.now())
			conn.commit()
		except:
			print("DEBUG: No data written to database")
		c.execute(result)
		
		
		conn.close()

		# print to Nextion Display

		#switch to 3rd screen
		port.write("page 3"+eof)

		#create string for down/up output
		mtdn = "{}/{}".format(multithread.down,multithread.up)
		stdn = "{}/{}".format(singlethread.down,singlethread.up)

		#print to display
		port.write('page3.mtdn.txt="'+mtdn+'"'+eof)
		port.write('page3.stdn.txt="'+stdn+'"'+eof)
		port.write('page3.mtlatency.txt="'+str(multithread.latency)+'"'+eof)
		port.write('page3.stlatency.txt="'+str(singlethread.latency)+'"'+eof)
		port.write('page3.lanip.txt="'+lanIP+'"'+eof)

		print("DEBUG:Execution completed at ",datetime.datetime.now()) 
		# Wait before
		print("DEBUG:Entering wait loop at ",datetime.datetime.now()) 
		time.sleep(3600)

		#dim the screen
		port.write("dim=25" + eof)

		print("DEBUG: Starting Loop at {}".format(datetime.datetime.now()))

if __name__ == "__main__":
	main()
