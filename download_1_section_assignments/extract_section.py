#!/usr/bin/env python3

from __future__ import annotations
from os.path import dirname, abspath
import os
import shutil
import sys

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
    with open(dirname(abspath(__file__)) + '/students.txt', 'r') as f:
        students = f.readlines()
        for i, student in enumerate(students):
            try:
                students[i] = students[i].replace(',', '').strip().lower()
                students[i] = (students[i])[ : students[i].index(' ')] #remove middle name
            except ValueError:
                pass
    return students

def make_dir(dir: str) -> None:
    '''
    Makes the directory if it doesnt exist. Raises error if the directory is already populated 
    dir -- directory we want to make
    '''
    if os.path.isdir(dir):
        student_files = os.listdir(dir)
        if 'ProposalPaperGraded' in student_files[0]:
            print("You've already extracted the files. Check the 'wanted_submissions' directory.")
            sys.exit(1)
    else:
        os.mkdir(dir)

def get_extension(file: str) -> str:
    '''
    returns the file extension of a file
    file -- str representation of the file path
    '''
    return file[file.index('.') : ]

def rename_files(wanted_dir: str) -> None:
    '''
    renames the files in wanted_submissions dir to just name plus assignment name 
    wanted_dir -- str path to dir were only students we want assignments from
    '''
    student_files = os.listdir(wanted_dir)
    for file in student_files:
        old_file = os.path.join(wanted_dir, file)
        new_file = os.path.join(wanted_dir, file[ : file.index('_')] + 'ProposalPaperGraded' + get_extension(file))
        os.rename(old_file, new_file)

def extract_submissions(submissions: str, wanted_dir:str) -> None:
    '''
    extracts all of the files from the submissions directory to a new directory 
    called 'wanted_submissions'
    submissions -- str path to all student submissions
    wanted_dir -- str path to dir were only students we want assignments from
    '''
    student_files = os.listdir(submissions)
    for i, sfile in enumerate(student_files):
        for student in get_students():
            if student in sfile:
                shutil.copyfile(submissions + sfile, wanted_dir + sfile)

def main():    
    submissions = dirname(abspath(__file__)) + '/submissions/'
    wanted_dir = dirname(abspath(__file__)) + '/wanted_submissions/'

    make_dir(wanted_dir)
    extract_submissions(submissions, wanted_dir)
    rename_files(wanted_dir)

if __name__ == '__main__':
    main()