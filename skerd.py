import json
import time
import datetime
import os
import shutil
import selenium
import selenium.webdriver.support.ui as ui
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from pprint import pprint
from datetime import timedelta

driver = webdriver.Firefox()
driver.implicitly_wait(5)

def makeURL(fips):
	url = 'https://eapps.courts.state.va.us/gdcourts/caseSearch.do?fromSidebar=true&searchLanding=searchLanding'
	searchType='&searchType=hearingDate&'
	searchDivision='searchDivision=T&search'
	num = 'FipsCode=' + fips + '&curentFipsCode=' + fips
	result = url+searchType+searchDivision+num
	return result

#want to return a list of dates to lookup. 60 days before todays date && 60 days after
def lookupDates(today):
	dates = []
	reverse = today + timedelta(60)
	for x in range(120):
		reverse -= timedelta(days=1)
		if reverse.weekday() < 5:
			dates.append(reverse)
	return dates

def lookupDates2(today):
	dates = []
	reverse = today + timedelta(3)
	for x in range(3):
		reverse -= timedelta(days=1)
		if reverse.weekday() < 5:
			print(reverse)
			dates.append(reverse)
	return dates

def getGridRows(gridrows):
	
	print(len(gridrows))
	myJSONList = []
	count = 1
	while (count < len(gridrows)):
		data = {}
		data['case'] = gridrows[count].text
		# print(gridrows[count].text)
		count+=1
		data['defendant'] = gridrows[count].text
		# print(gridrows[count].text)
		count+=1
		data['complainant'] = gridrows[count].text
		# print(gridrows[count].text)
		count+=1
		data['charge'] = gridrows[count].text
		# print(gridrows[count].text)
		count+=1
		data['hearing'] = gridrows[count].text
		# print(gridrows[count].text)
		count+=1
		data['result'] = gridrows[count].text
		# print(gridrows[count].text)
		count+=2
		myJSONList.append(data)
	return myJSONList

def makeFile(date, courtData):
	filename = str(date) + ".json"
	src = "./" + filename
	dest = "./" + name + '/' + filename
	with open(filename, 'w') as outfile:
		json.dump(courtData, outfile)	
	shutil.move(src, dest)


#-----> too scerd to run code below this line
with open('courts.json') as data_file:
	data = json.load(data_file)
for d in data:
	fips = d["fips"]
 	name = d["name"]
	os.mkdir(name)
 	url = makeURL(fips)
 	driver.get(url)
 	driver.add_cookie({'name':'JSESSIONID', 'value':'0000GwK2_Ta93lierLXjFw9BBgZ:1962kblff', 'path':'/'})
 	driver.get(url)
 	hearing = driver.find_element_by_id("txthearingdate")

	dates = lookupDates2(datetime.date.today() - timedelta(1))
	for date in dates:
		url = makeURL(fips)
		driver.get(url)
		courtData = []
		format = date.strftime("%m") + str("/") + date.strftime("%d") + str("/") + date.strftime("%Y")
		hearing = driver.find_element_by_id("txthearingdate")
		hearing.clear()
		hearing.send_keys(format)
		submit = driver.find_element_by_name("caseSearch")
		submit.click(); 
		nextURL = 'https://eapps.courts.state.va.us/gdcourts/caseSearch.do'
		try:
			gridrows = driver.find_elements_by_class_name("gridrow");
			courtData.append(getGridRows(gridrows))
			try:
				next = driver.find_element_by_name("caseInfoScrollForward")
			except NoSuchElementException:
				next = None
 		except NoSuchElementException:
			print ("no data for this date")
			

		while next is not None:
			#driver.get(nextURL)
			try:
				next = driver.find_element_by_name("caseInfoScrollForward")
				next.click()
				next = driver.find_element_by_name("caseInfoScrollForward")
			except NoSuchElementException:
				print ("finished all pages for current date")
				next = None
			try:
				gridrows = driver.find_elements_by_class_name("gridrow");
				courtData.append(getGridRows(gridrows))
			except:
				print ("no data for this page")
		makeFile(date, courtData)
	break
