#!/usr/bin/env python3

import json
import os
import re
import sys
from dataclasses import dataclass
from canvasapi import Canvas, requester
import urllib.request

# Docs
# https://canvasapi.readthedocs.io/en/stable/index.html
# https://canvas.instructure.com/doc/api/index.html
# https://github.com/ucfopen/canvasapi

@dataclass
class Student:
    name: str
    ID: str

def validate():
    with open("Auth.json") as f:
        d = json.load(f)
    try:
        API_URL = d["API_URL"]
        API_KEY = d["API_KEY"]
        return Canvas(API_URL, API_KEY)
    except KeyError:
        print('There was an error accessing the API_URL or API_KEY inside of the "Auth.json" file')
        print("Enter each inside of double quotes, i.e.")
        print('"https://canvas.wisc.edu/"')
        sys.exit(1)

def desired_course(canvas):
    #return a Course object that the user picked
    courses = active_canvas_courses(canvas)
    print(f"There are {len(courses)} active courses in your Canvas page in which you are a teacher")
    print("Which would you like to choose?")
    print('''Note: Some old classes may be listed here. 
        If they are, that means they are still listed as active under Canvas - 
        which there is nothing I can do about\n''')
    for i, course in enumerate(courses):
        print(f"({i}) --" , course.name)
    try:
        choice = int(input("> "))
        return courses[choice]
    except (ValueError, IndexError) as e:
        print("Enter a digit corresponding to the course")

def active_canvas_courses(canvas):
    #return a list of all active Canvas courses which you are a ta or teacher
    current = []
    courses = canvas.get_courses()
    types = ["teacher", "ta"]
    for course in courses:
        try:
            #TODO this is pretty ugly, but ok for now..
            if ( 
                course.enrollments[0]["enrollment_state"] == "active" 
                and 
                course.enrollments[0]["type"] in types
            ):
                current.append(course)    
        except AttributeError:
            #There is a strange issue where old Canvas classes raise this error, idk why..
            pass       
    return current   

def desired_section(course):
    #return a Section object corresponding to the user input
    print(f"What section of {course.name} do you want to get?")
    sections = course.get_sections()
    for i, section in enumerate(sections):
        print(f"({i}) --" , section)
    try:
        choice = int(input("> "))
        return sections[choice]
    except (ValueError, IndexError) as e:
        print("Enter a digit corresponding to the section")

def populate_enrollment(section):
    #return a list of Student objects (name, id) in the desired section
    students = []
    enrollments = section.get_enrollments()
    # TODO only get students that are enrolled
    for enrollment in enrollments:
        if enrollment.role == "StudentEnrollment":
            #print(enrollment.user_id)
            name = enrollment.user["name"]
            name = name.title().replace(" ", "")
            ID = enrollment.user["id"]
            students.append(Student(name, ID))
    return students

def get_published_assignments(course):
    #TODO get year without name
    #TODO embellish prompt
    # lists out all of the published assignments for user input
    assignments = course.get_assignments()
    print("What assignment do you want to download the files for?")
    #TODO fix this bug with hidden assignments
    for i, assignment in enumerate(assignments):
        if assignment.published:
            print(f"({i}) --" , assignment.name)
    try:
        choice = int(input("> "))
        return assignments[choice]
    except (ValueError, IndexError) as e:
        print("Enter a digit corresponding to the published assignment.")

def download_assignments(students, assignment):
    #downloads assignments into ./submissions directory
    print("What do you want to call the name of the file for each student?")
    name = input("> ")
    os.makedirs("./submissions", exist_ok=True)
    os.makedirs("./submissions/" + name, exist_ok=True)
    for i, student in enumerate(students, 1):
        try:
            file_name = str(assignment.get_submission(student.ID).attachments[0])
            extension = file_name[file_name.index(".") : ]
            submission_url = assignment.get_submission(student.ID).attachments[0].url
            # TODO beautify name
            urllib.request.urlretrieve(submission_url, f"./submissions/{name}/{student.name}_{name}_graded{extension}")
            #say if the number of submission is not the same as the acualy amout of people
            print(f"downloading file {i} of {len(students) - 1} submissions", end = "\r")
        except (IndexError, requester.ResourceDoesNotExist) as e:
            #no submission or member of teaching team
            pass

def main():
    canvas = validate()
    course = desired_course(canvas)
    section = desired_section(course)
    students = populate_enrollment(section)
    assignment = get_published_assignments(course)
    download_assignments(students, assignment)
    
    # TODO bug for students len because teachers 
    # TODO fix tell where it is being downloaded
    print(f"Finished :)")

if __name__ == "__main__":
    main()