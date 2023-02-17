#!/usr/bin/env python3

import json
import os
import pathlib
import sys
import urllib.request

from dataclasses import dataclass
from canvasapi import Canvas, requester

#TODO some assignments dont have submissions to them, can I still get them?

# Docs
# https://canvasapi.readthedocs.io/en/stable/index.html
# https://canvas.instructure.com/doc/api/index.html
# https://github.com/ucfopen/canvasapi

def validate():
    with open("Auth.json", "r") as f:
        d = json.load(f)
    try:
        API_URL = d["API_URL"]
        API_KEY = d["API_KEY"]
        return Canvas(API_URL, API_KEY)
    except KeyError:
        print('There was an error accessing the API_URL or API_KEY inside of the "Auth.json" file.')
        print("Enter each inside of double quotes, i.e.")
        print('"https://canvas.wisc.edu/"')
        sys.exit(1)

def desired_course(canvas):
    #return a Course object that the user picked
    courses = active_canvas_courses(canvas)
    print(f"There are {len(courses)} active courses in your Canvas page in which you are a teacher.")
    print('''Note: Some old classes may be listed here. 
          If they are, that means they are still listed as active under Canvas. \n''')
    for i, course in enumerate(courses):
        print(f"({i}) --" , course.name)
    while True:
        try:
            print("\nWhich class would you like to choose?")
            choice = int(input("> "))
            if choice < 0:
                print("Negative course ehh?")
                continue
            print()
            return courses[choice]
        except (ValueError, IndexError):
            print("Enter a digit corresponding to the course")

def active_canvas_courses(canvas):
    #return a list of all active Canvas courses which you are a ta or teacher
    current = []
    # TODO change to a set not a list
    courses = canvas.get_courses()
    types = ["teacher", "ta"]
    for course in courses:
        try:
            #TODO this is pretty ugly, but ok for now..
            if ( 
                # One enrollment is a list of one dict
                course.enrollments[0]["enrollment_state"] == "active" 
                and 
                course.enrollments[0]["type"] in types
            ):
                current.append(course)    
        except AttributeError:
            #There is a strange issue where old Canvas classes raise this error, idk why..
            pass       
    return current   

def get_all_students(course):
    # TODO no need to make my own dataclass..
    all_students = []
    students = course.get_users(
        enrollment_type=["student"],
        #enrollment_state=['active', 'invited']
    )
    for student in students:
        all_students.append(Student(student.name, student.id))
    return all_students

def desired_section(course):
    #return a Section object corresponding to the user input
    sections = course.get_sections()
    for i, section in enumerate(sections):
        print(f"({i}) --" , section)
    while True:
        try:
            print(f"\nWhat section of {course.name} do you want to get?")
            print("You can leave this blank if you want to get all sections.")
            choice = input("> ")
            print()
            if choice == "":
                # No desired section
                return None
            else:
                #choice = int(choice) # TODO this is a bit hacky
                return sections[int(choice)]
        except (ValueError, IndexError):
            print("Enter a digit corresponding to the section")

@dataclass
class Student: 
    name: str
    ID: str

def populate_enrollment(section):
    #return a list of Student objects (name, id) in the desired section
    students = []
    enrollments = section.get_enrollments()
    for enrollment in enrollments:
        if enrollment.role == "StudentEnrollment":
            name = enrollment.user["name"].title().replace(" ", "")
            ID = enrollment.user["id"]
            students.append(Student(name, ID))
    return students

def get_published_assignments(course):
    #TODO this hangs for a bit
    assignments = course.get_assignments()
    print("Please wait. Sometimes this can hang for a little while.")
    for i, assignment in enumerate(assignments):
        if assignment.published:
            print(f"({i}) --" , assignment.name)
    while True:
        try:
            print("\nWhat assignment do you want to download the files for?")
            choice = int(input("> "))
            return assignments[choice]
        except (ValueError, IndexError):
            print("Enter a digit corresponding to the published assignment.")

def download_assignments(students, assignment):
    #downloads assignments into ./submissions directory
    print("\nWhat do you want to call the name of the file for each student?")
    assignment_name = input("> ")
    os.makedirs("./submissions", exist_ok=True)
    os.makedirs("./submissions/" + assignment_name, exist_ok=True)
    print()
    for i, student in enumerate(students, 1):
        try:
            file_name = str(assignment.get_submission(student.ID).attachments[0])
        except (IndexError, requester.ResourceDoesNotExist):
            sys.stdout.write("\033[K") # Clear to the end of line
            print(f"No submission from {student.name}")
            continue
        #TODO Fix this. Bug when . in file but not extension lol
        #get the last . from the file not the first :O
        extension = pathlib.Path(file_name).suffixes[-1] 
        submission_url = assignment.get_submission(student.ID).attachments[0].url
        urllib.request.urlretrieve(submission_url, f"./submissions/{assignment_name}/{student.name}_{assignment_name}_graded{extension}")
        print(f"downloading submission {i} of {len(students) - 1} students", end = "\r")
    print(f"Files have been downloaded to submissions/{assignment_name}")

def main():
    canvas = validate()
    course = desired_course(canvas)
    section = desired_section(course)

    #TODO this is a bit janky..
    try: #get students from one section
        students = populate_enrollment(section)
    except AttributeError:
        #get students from all sections
        students = get_all_students(course)
    
    assignment = get_published_assignments(course)
    download_assignments(students, assignment)

if __name__ == "__main__":
    sys.exit(main())
