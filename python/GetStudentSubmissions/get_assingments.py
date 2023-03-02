#!/usr/bin/env python3

import json
import os
import pathlib
import shutil
import sys
import urllib.request
from dataclasses import dataclass

from canvasapi import Canvas, requester

#TODO some assignments dont have submissions to them, can I still get them?
#TODO format name for all sections as well
#TODO organize download for all section choice

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
    If they are, that means they are still listed as active under Canvas.\n''')
    for i, course in enumerate(courses):
        print(f"({i}) --" , course.name)
    while True:
        try:
            print("\nWhich class would you like to choose?")
            choice = int(input("> "))
            if choice < 0: continue
            print()
            return courses[choice]
        except (ValueError, IndexError):
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
        all_students.append(Student(student.name.title().replace(" ", ""), student.id, "TODO"))
    return all_students

def get_students_from_section(course):
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
                return get_all_students(course)
            else:
                return populate_enrollment(sections[int(choice)])
        except (ValueError, IndexError):
            print("Enter a digit corresponding to the section")

@dataclass
class Student: 
    name: str
    ID: str
    group: str

def populate_enrollment(section):
    #return a list of Student objects (name, id, group = "unassigned") in the desired section
    students = []
    enrollments = section.get_enrollments()
    for enrollment in enrollments:
        if enrollment.role == "StudentEnrollment":
            name = enrollment.user["name"].title().replace(" ", "")
            ID = enrollment.user["id"]
            students.append(Student(name, ID, "unassigned"))
    return students

def get_published_assignments(course):
    #TODO this hangs for a bit
    assignments = course.get_assignments()
    published_assignments = []
    [published_assignments.append(a) for a in assignments if a.published]
    for i, assignment in enumerate(published_assignments):
        print(f"({i}) --" , assignment.name)
    while True:
        try:
            print("\nHere are all of the published assignments to the class.")
            print("What assignment do you want to download the files for?")
            choice = int(input("> "))
            if choice < 0: continue
            return published_assignments[choice]
        except (ValueError, IndexError):
            print("Enter a digit corresponding to the published assignment.")

def move_resources(student_dir):
    #Move all of the resources in the resource directory into the student_dir
    name = student_dir.split("/")[-1]
    resources = os.listdir("./resources")
    for r in resources:
        shutil.copyfile("./resources/" + r, student_dir + "/" + name + r)

def download_assignments(students, assignment):
    #downloads assignments into ./submissions directory
    print("\nWhat do you want to call the name of the file for each student?")
    assignment_name = input("> ")
    os.makedirs("./submissions/" + assignment_name, exist_ok=True)
    print()
    for i, student in enumerate(students, 1):
        group_dir = f"./submissions/{assignment_name}/{student.group}"
        os.makedirs(group_dir, exist_ok=True)
        student_dir = f"{group_dir}/{student.name}"
        os.makedirs(student_dir, exist_ok=True)
        try:
            file_name = str(assignment.get_submission(student.ID).attachments[0])
        except (IndexError, requester.ResourceDoesNotExist):
            sys.stdout.write("\033[K") # Clear to the end of line
            print(f"No submission from {student.name}")
            continue
        extension = pathlib.Path(file_name).suffixes[-1] 
        title = f"{student_dir}/{student.name}_{assignment_name}_graded{extension}"
        submission_url = assignment.get_submission(student.ID).attachments[0].url
        urllib.request.urlretrieve(submission_url, title)
        move_resources(student_dir)
        print(f"downloading submission {i} of {len(students) - 1} students", end = "\r")
    print(f"Files have been downloaded to {os.path.dirname(os.path.abspath(__file__))}/submissions/{assignment_name}")

def add_groups(course, students):
    #Adds the groups to the student objects
    # TODO This is horrible inneficient
    groups = course.get_groups()
    for group in groups:
        for user in group.get_users():
            for student in students:
                if student.ID == user.id:
                    student.group = group.name
    return students 

def main():
    canvas = validate()
    course = desired_course(canvas)
    students = get_students_from_section(course)
    print("Please wait. Sometimes this can hang for a little while.")
    students = add_groups(course, students)
    assignment = get_published_assignments(course)
    download_assignments(students, assignment)

if __name__ == "__main__":
    sys.exit(main())