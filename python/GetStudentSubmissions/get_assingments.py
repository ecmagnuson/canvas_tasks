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

def validate():
    #Validate the url and key and return a canvas object
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

def get_a_course(canvas):
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

def get_course_section(course):
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
    group: str

def get_section_students(section, all_students):
    #return a list of Student objects (name, id, group = "unassigned") in the desired section
    section_students = []
    if section == None:
        return all_students
    enrollments = section.get_enrollments()
    for enrollment in enrollments:
        if enrollment.role == "StudentEnrollment":
            name = enrollment.user["name"].title().replace(" ", "")
            ID = enrollment.user["id"]
            section_students.append(Student(name, ID, "unassigned"))
    return add_section_groups(all_students, section_students)

def get_published_assignments(course):
    #Return a list of assignments for the course that are published
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
    try:
        resources = os.listdir("./resources")
        for r in resources:
            shutil.copyfile("./resources/" + r, student_dir + "/" + name + r)
    except FileNotFoundError:
        return 

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

def get_course_students(course):
    #reurn a list of all Student(name, id, group) in a course
    print("Collecting students..")
    students = []
    groups = course.get_groups()
    for group in groups:
        for user in group.get_users():
            name = user.name.title().replace(" ", "")
            students.append(Student(name, user.id, group.name))
    return students

def add_section_groups(all_students, section_students):
    #Adds the group from all_setends to the section_students
    for s in section_students:
        for a in all_students:
            if s.name == a.name:
                s.group = a.group
    return section_students

def main():
    canvas = validate()
    course = get_a_course(canvas)
    all_students = get_course_students(course)
    section = get_course_section(course)
    section_students = get_section_students(section, all_students)
    assignment = get_published_assignments(course)
    download_assignments(section_students, assignment)

if __name__ == "__main__":
    sys.exit(main())