#schedule.txt:
#    A table containing applications, command line flags, start times, stop times, whether the application is enabled,
#    and the days of the week the application runs. Days of the week are read as follows:
#    1,4-7 = Sunday, Wednesday, Thursday, Friday, Saturday
#    *     = Every day of the week

#apps#.txt:
#    A date to consider and an unsorted list of application names

#Create a Python 3 program that does the following:
#    1.  Takes the path to a schedule file, the path to an app file, and the path to an output file as command line arguments
#    2.  Writes a csv of the applications that would run on the date in the app file as well as their options,
#       start times, and stop times

#EXAMPLE
#python3 script.py schedule.txt apps1.txt example.txt

#You can assume the apps files will never contain an application that is not present in the schedule file and that
#neither input will contain malformed or invalid data

#--Does not say that not all inputs will be put in. Needs checked.

#!/usr/bin/python
import sys
import pandas
import os
import datetime
import pathlib

datesDict = { 'SUNDAY': '1',
'MONDAY': '2',
'TUESDAY': '3',
'WEDNESDAY': '4',
'THURSDAY': '5',
'FRIDAY': '6',
'SATURDAY': '7'}

def main():
	if(len(sys.argv) == 4):
		#Get schedule file and output file locations.
		outputfile = pathlib.Path(sys.argv[3])
		schedulefile = pathlib.Path(sys.argv[1])
		appFile2 = pathlib.Path(sys.argv[2])
		if(not schedulefile.exists() or not appFile2.exists()):
			print("One of the two files given does not exist. Please try again with a file that exists.")
			sys.exit(2);

		df = pandas.read_table(schedulefile, index_col=0, sep='|',header=0,skiprows=[1],skipinitialspace=True,keep_default_na=False)
		df.columns = df.columns.str.replace('%',' ',regex=True)
		df.columns = df.columns.str.strip()

		#Removes 'Unnamed' column
		dff = df[df.columns[0:6]]

		appArray = []
		counter = 0
		appDate = ''

		#Get Date and Application names from application file given.
		appfile = open(sys.argv[2], 'r')
		for line in appfile:
			line = line.rstrip("\n")
			if (counter == 0):
				appDate = line
				counter += 1
			else:
				appArray.append(line)

		#Sets a datetime object to the given date from the application file.
		#Then transforms it into the Day of the Week and sets to uppercase.
		dte = datetime.datetime.strptime(appDate,'%Y-%m-%d')
		dayOfWeek = dte.strftime("%A").upper()

		#Creates a dataframe from table read in, day of week, and list of applications given
		#Then writes it to a CSV file in current directory
		df = createDataframe(dff, dayOfWeek, appArray)
		writeCsv(df,outputfile)

	#Not correct # of arguments.
	else:
		print("# of arguments is " + str(len(sys.argv)-1) + ". Incorrect number of arguments. Please enter schedule.txt, the apps.txt being used, and the output file's name as arguments.")

		sys.exit(2);

def createDataframe(df, appDate, appArray):
	numberedDate = datesDict[appDate]

	pattern = '|'.join(appArray)

	#'contains' works, but 'isin' does not. Unsure why as both should work from what I've seen.
	#Searchs dataframe from applications that were in the application file given
	updatedDf = df[df['Application'].str.contains(pattern)]

	#temporary copy to work with schedule in friendly terms
	copiedDf = updatedDf.copy()
	
	#IF DISABLED=TRUE MEANS DO NOT RUN, REMOVE ROWS HERE BEFORE SENDING TO UPDATE SCHEDULE.
	copiedDf = copiedDf[copiedDf['Disabled'].str.strip() == 'false']

	#updated to the schedules that are correct for the date
	copiedDf['Schedule'] = copiedDf['Schedule'].apply(updateSchedule,args=numberedDate)
	tmpScheduleDf = copiedDf[copiedDf['Schedule'] != '0']

	#Make new DF from applications that are supposed to run
	resultDf = updatedDf[updatedDf['Application'].isin(tmpScheduleDf['Application'])].copy()
	#Drop columns that end user does not wish/need to see
	resultDf = resultDf.drop(['Disabled','Schedule'],axis=1)

	#removes any extra white space cells may carry
	dfTrimmed = resultDf.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

	return dfTrimmed


def updateSchedule(times, dateNumber):
	result = []

	for part in times.split(','):
		#If Schedule is *
		if (part.strip() == "*"):
			result.append(part.strip())
		#If Schedule has range in it
		elif '-' in part:
			a, b = part.split('-')
			a, b = int(a), int(b)
			result.extend(list(range(a, b + 1)))
		#If Schedule single integer
		else:
			a = int(part)
			result.append(a)

	#Set flag if the scheduled date is not the running date given
	if(int(dateNumber) not in result and "*" not in result):
		#Easily removeable since not a list.
		result = '0'


	return result

#Writes CSV based off of dataframe and filename.
def writeCsv(finalDf,filename):
	finalDf.to_csv(filename,index=False,header=False)


if __name__=="__main__":
	main()