# The code is depant on a few packages, sich as the google api and oayth 2
# These import statements gets the packages required for the code to run
from __future__ import print_function
from operator import contains
import time

import os.path
import iso8601
import datetime
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

import httplib2
import googleapiclient.http
import googleapiclient.errors
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

# Variables
classes = []
emptyList = []
allClasses = []
allClassIds = []
numberOfClasses = []
classAssignments = []
flags = None

#The scopes are basically the permissions for what the code needs to use.
SCOPES = 'https://www.googleapis.com/auth/classroom.coursework.me.readonly', \
            'https://www.googleapis.com/auth/classroom.courses.readonly',

CLIENT_SECRET_FILE = 'credentials.json'
APPLICATION_NAME = 'Better Classroom Notifications Beta'

# This part of the code deals with Google Authentication
def getCredentials():
    """Gets valid user credentials from storage.
    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.
    Returns:
        Credentials, the obtained credential.
    """
    cwd = os.getcwd()
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(cwd, '.credentials')
    credential_path = os.path.join(credential_dir, 'BCN_Beta_userCredentials.json')

    try:
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
            credential_path = os.path.join(credential_dir, 'BCN_Beta_userCredentials.json')
        store = Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
            flow.user_agent = APPLICATION_NAME
            credentials = tools.run_flow(flow, store, flags)
            print('\nStoring credentials to ' + credential_path)
        return credentials
    except:
        print("\nError: 'credentials.json' was not found. Please go to 'https://www.youtube.com/watch?v=1WwLPcVaYxY&t=20s' and follow the instructions there to create it. When created, place the file into the same folder as the code and the BCNBeta.exe. You may receive an error when creating the credentials.json file, try again and it should work. If the problem persists, please email 'bcnbetahelp@gmail.com' with your name and a screenshot of the error.\n")

# These 2 functions converts the google classroom time format to a readable time format
def creationTime(date_string):
  iso_time = iso8601.parse_date(date_string)
  return iso_time.strftime("Created: %d %B, %Y - %H:%M")

def dueDate(date, time):
    year = date['year']
    month = date['month']
    day = date['day']
    hour = time['hours']
    minute = time['minutes']

    date_str = datetime.datetime(year, month, day, hour, minute)
    final_date = date_str.strftime("Due Date: %d %B, %Y - %H:%M")

    return final_date

# This code gets the state of the assignment
def studentSubmissionState(course_id, coursework_id, user_id):
    credentials = getCredentials()
    http = credentials.authorize(httplib2.Http())
    
    submissions = []
    page_token = None

    try:
        service = build('classroom', 'v1', http=http)
        while True:
            coursework = service.courses().courseWork()
            response = coursework.studentSubmissions().list(
                pageToken=page_token,
                courseId=course_id,
                courseWorkId=coursework_id,
                userId=user_id).execute()
            submissions.extend(response.get('studentSubmissions', []))
            page_token = response.get('nextPageToken', None)
            courseworkresults = service.courses().courseWork().list(
                courseId=course_id, pageSize=1000).execute()
            coursework2 = courseworkresults.get('courseWork', [])
            if not page_token:
                break
        for coursework in coursework2:
            if not submissions:
                print('No student submissions found.')
            for submission in submissions:
                data = [
                    "State: " + submission.get('state')]
                return data
    except HttpError as error:
        print(f"An error occurred: {error}")
    return submissions

# This code gets the grade given to the assignment
def studentSubmissionGrade(course_id, coursework_id, user_id):
    credentials = getCredentials()
    http = credentials.authorize(httplib2.Http())

    submissions = []
    page_token = None

    try:
        service = build('classroom', 'v1', http=http)
        while True:
            coursework = service.courses().courseWork()
            response = coursework.studentSubmissions().list(
                pageToken=page_token,
                courseId=course_id,
                courseWorkId=coursework_id,
                userId=user_id).execute()
            submissions.extend(response.get('studentSubmissions', []))
            page_token = response.get('nextPageToken', None)
            courseworkresults = service.courses().courseWork().list(
                courseId=course_id, pageSize=1000).execute()
            coursework2 = courseworkresults.get('courseWork', [])
            if not page_token:
                break
        for coursework in coursework2:
            if not submissions:
                print('No student submissions found.')
            for submission in submissions:
                data = [f"Grade: {submission.get('assignedGrade')}"]
                if data == "Grade: None":
                    return "No grade found."
                else:
                    return data
    except HttpError as error:
        print(f"An error occurred: {error}")
    return submissions

# This is the main function. It scans through the user's courses and gets its name and id
# The name of the course is given to the user, but the course id stays within the code
def getCourses():
    credentials = getCredentials()
    http = credentials.authorize(httplib2.Http())

    try:
        service = build('classroom', 'v1', http=http)
        
        results = service.courses().list(pageSize=100).execute()
        courses = results.get('courses', [])

        if not courses:
            print('No courses found.')
            return
        print("\nBelow, is a list of all the classes this system recognizes.\n")
        time.sleep(2)
        indexNumber = 0
        for course in courses:
            numberOfClasses.append(indexNumber)
            classId = [course.get('id')]
            print(f" {indexNumber}. {course.get('name')} {course.get('alternateLink')}")
            allClasses.append(f"{indexNumber}. {classes},")
            allClassIds.append(classId)
            indexNumber += 1
        completed = False
        while not completed:
            try:
                currentCourseId = int(input("\nPlease enter the number next to the class you would like to get information from: "))
                if currentCourseId not in numberOfClasses:
                    print("\nThat number does not have an assigned class")
                    completed = False
                else:
                    completed = True
            except:
                print("\nPlease enter an integer. For example, if you want to get information from the first class, enter '0'")
        checkInput(str(allClassIds[currentCourseId]).removeprefix("['").removesuffix("']"))
    except HttpError as error:
        print('An error occurred: %s' % error)

def getCoursesAlt():
    try:
        completed = False
        while not completed:
            try:
                currentCourseId = int(input("\nPlease enter the number next to the class you would like to get information from: "))
                
                if currentCourseId not in numberOfClasses:
                    print("\nThat number does not have an assigned class")
                    completed = False
                else:
                    completed = True
            except:
                print("\nPlease enter an integer. For example, if you want to get information from the first class, enter '0'")    
        checkInput(str(allClassIds[currentCourseId]).removeprefix("['").removesuffix("']"))
    except HttpError as error:
        print(' An error occurred: %s' % error)

#This function takes the id from getCourses and provides the user with the assignment information
def getAssignments(course_id, state):
    credentials = getCredentials()
    http = credentials.authorize(httplib2.Http())

    try:
        service = build('classroom', 'v1', http=http)
        courseworkresults = service.courses().courseWork().list(
            courseId=course_id, pageSize=10000).execute()
        coursework = courseworkresults.get('courseWork', [])
        if not coursework:
            print('No coursework found.')
        print('\nThe code will return the information in the following format:\n')
        time.sleep(1)
        print('Assignment name, the assignment id, the creation time, the due date, the state of the assignment, and the grade.')
        time.sleep(1)
        print('\n------------------------------------------------\n')
        print("Locating Information... (May take a while)\n")
        print("If nothing is returned, it means that no assignments were found with the parameters you have selected.\n")
        for coursework in coursework:
            try:
                assingments = [
                    f"Title: {coursework['title']}",
                    f"ID: {coursework['id']}",
                    creationTime(coursework['creationTime']),
                    dueDate(coursework['dueDate'], coursework['dueTime']),
                ]
                Info = [
                    assingments + studentSubmissionState(course_id, assingments[1].removeprefix("ID: "), "me") + studentSubmissionGrade(course_id, assingments[1].removeprefix("ID: "), "me")
                ]
                if state in studentSubmissionState(course_id, assingments[1].removeprefix("ID: "), "me"):
                    classAssignments.append(Info)
                    strInfo = ' '.join(map(str, Info)).removeprefix("[").removesuffix("]")
                    print(strInfo, "\n")
                elif state == 'ALL':
                    classAssignments.append(Info)
                    strInfo = ' '.join(map(str, Info)).removeprefix("[").removesuffix("]")
                    print(strInfo, "\n")
            except:
                reduced_assingments = [f"Title: {coursework['title']}", f"ID: {coursework['id']}",
                                       'Due date was not specified by the teacher', creationTime(coursework['creationTime'])]
                Info = [
                    reduced_assingments + studentSubmissionState(course_id, reduced_assingments[1].removeprefix("ID: "), "me") + studentSubmissionGrade(course_id, reduced_assingments[1].removeprefix("ID: "), "me")
                ]
                if state in studentSubmissionState(course_id, reduced_assingments[1].removeprefix("ID: "), "me"):
                    classAssignments.append(Info)
                    strInfo = ' '.join(map(str, Info)).removeprefix("[").removesuffix("]")
                    print(strInfo, "\n")
                elif state == 'ALL':
                    classAssignments.append(Info)
                    strInfo = ' '.join(map(str, Info)).removeprefix("[").removesuffix("]")
                    print(strInfo, "\n")
        if classAssignments == emptyList:
            print("No assignments found in this classroom")
        

    except HttpError as error:
        print('An error occurred: %s' % error)

# This function asks the user for details about the assignments, then passes them through to getAssignments
def checkInput(course_id):
    completed = False
    print("\nWhat assignments would you like to see? Assignments that are turned in, returned, outstanding assignments? or all assignments?")
    print("Turned in assignments refer to assignments that have been turned in by you, but graded, whereas, returned assignments have a grade assigned to them\n")
    while not completed:      
        value = input("")
        if value == "outstanding" or value == "outstanding assignments" or value == "Outstanding" or value == "Outstanding assignments" or value == "Outstanding Assignments":
            getAssignments(course_id, 'State: CREATED')
            completed = True
        elif value == "returned" or value == "returned assignments" or value == "Returned" or value == "Returned assignments" or value == "Returned Assignments":
            getAssignments(course_id, 'State: RETURNED')
            completed = True
        elif value == "turned in" or value == "turned in assignments" or value == "Turned In" or value == "Turned in assignments" or value == "Turned In Assignments":
            getAssignments(course_id, 'State: TURNED_IN')
            completed = True
        elif value == "all" or value == "all assignments" or value == "All" or value == "All assignments" or value == "All Assignments":
            getAssignments(course_id, 'ALL')
            completed = True
        else:
            print("\nYour input was not recognizable. Please check your spelling, or try using one word in lowercase.")

def newListFunc():
    correctInput = False
    while correctInput == False:
        newList = input("\nWould you like to see the list again? (y/n)  ")
        if newList == "y" or newList == "Y":
            correctInput = True
            getCourses()
        elif newList == "n" or newList == "N":
            correctInput = True
            getCoursesAlt()
        else:
            correctInput = False
            print("\nYour input was unreadable, please use either 'y' to indicate 'yes', or 'n' to indicate 'no'")

if __name__ == '__main__':
    runTime = 0
    done = False
    while not done:
        if runTime < 1:
            runTime += 1
            correctInput = False
            print("\nHello and welcome to the Better Classroom Notifications(BCN) Beta program!")
            getCourses()
            while correctInput == False:             
                value = input("\nWould you like to see more information about another class? (y/n)  ")
                if value == "y" or value == "Y":
                    correctInput = True
                    newListFunc()
                elif value == "n" or value == "N":                  
                    done = True
                    correctInput = True
                else:
                  print("\nYour input was unreadable, please use either 'y' to indicate 'yes', or 'n' to indicate 'no'")
        else:
            runTime += 1
            while correctInput == False:
                value1 = input("\nWould you like to see more information about another class? (y/n)  ")
                if value1 == "y" or value1 == "Y":
                    correctInput = True
                    newListFunc()
                elif value1 == "n" or value1 == "N":
                    correctInput = True
                    break
                else:
                    print("\nYour input was unreadable, please use either 'y' to indicate 'yes', or 'n' to indicate 'no'")
