from __future__ import annotations
from os.path import dirname, abspath
import os
import shutil

def get_students():
    '''
    Returns a list of the students (format 'lastnamefirstname') from student.txt
    after removing upper case, commas, and the middle name from each student
    e.g. smithjohn
    '''
    with open('students.txt', 'r') as f:
        students = f.readlines()
        for i, student in enumerate(students):
            try:
                students[i] = students[i].replace(',', '').strip().lower()
                students[i] = (students[i])[ : students[i].index(' ')] #remove middle name
            except ValueError:
                pass
    return students

def extract_submission():
    submissions = dirname(abspath(__file__)) + '/submissions/'
    destination = dirname(abspath(__file__)) + '/wanted_submissions/'
    for file in os.listdir(submissions):
        for student in get_students():
            if student in file:
                shutil.copyfile(submissions + file, destination + file)

if __name__ == '__main__':
    extract_submission()