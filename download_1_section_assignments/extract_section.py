from __future__ import annotations
from os.path import dirname, abspath
import os
import shutil

def read_student_list() -> Lst[str]:
    students = []
    with open('students.txt', 'r') as f:
        for line in f.readlines():
            students.append(line)
    return students

def get_student_lastname() -> Lst[str]:
    students = read_student_list()
    student_lastnames = []
    for student in students:
        student_lastnames.append(student[ : student.index(',')].lower())
    return student_lastnames

def extract_submission():
    source = dirname(abspath(__file__)) + '/submissions/'
    destination = dirname(abspath(__file__)) + '/wanted_submissions/'
    directory_in_str = dirname(dirname(abspath(__file__)) + '/submissions/')
    students = get_student_lastname()
    for file in os.listdir(directory_in_str):
        for student in students:
            if student in file:
                shutil.copyfile(source + file, destination + file)
    return 'files added :D'

if __name__ == '__main__':
    extract_submission()