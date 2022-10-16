#!/usr/bin/env python3

from __future__ import annotations
from os.path import dirname, abspath
import os
import shutil

'''
reads the students from students.txt and extracts their assignments from
the submissions directory into the wanted_submissions directory.
'''

def get_students() -> Lst[str]:
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

def make_dir(dir: str) -> None:
    '''Makes the directory if it doesnt exist '''
    if os.path.isdir(dir):
        pass
    else:
        os.mkdir(dir)

def rename_files():
    submissions = dirname(abspath(__file__)) + '/wanted_submissions/'
    student_files = os.listdir(submissions)

    for file in student_files:
        old_file = os.path.join(submissions, file)
        new_file = os.path.join(submissions, file[ : file.index('_')] + 'ProposalPaperGraded')
        os.rename(old_file, new_file)

def extract_submissions() -> None:
    '''
    extracts all of the files from the submissions directory to a new directory 
    called 'wanted_submissions'
    '''
    submissions = dirname(abspath(__file__)) + '/submissions/'
    destination = dirname(abspath(__file__)) + '/wanted_submissions/'
    student_files = os.listdir(submissions)
    students = get_students()
    make_dir(destination)

    for i, sfile in enumerate(student_files):
        for student in students:
            if student in sfile:
                shutil.copyfile(submissions + sfile, destination + sfile)

def main():
    extract_submissions()
    rename_files()

if __name__ == '__main__':
    main()
    
    