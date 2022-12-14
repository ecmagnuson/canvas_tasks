package main

import (
	"archive/zip"
	"bufio"
	"io"
	"log"
	"os"
	"path/filepath"
	"strconv"
	"strings"
)

// makeDir creates a directory given relative string path
func makeDir(dirname string) {
	dir := filepath.Join(".", dirname)
	err := os.MkdirAll(dir, os.ModePerm)

	if err != nil {
		logError(err.Error())
		log.Fatal(err)
	}
}

// readStudents returns a slice of students from students.txt after removing commas and uppercase letters
func readStudents() []string {
	var students []string
	file, err := os.Open("../resources/students.txt")
	if err != nil {
		logError(err.Error())
		log.Fatal(err)
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		student := scanner.Text()
		student = strings.ToLower(student)
		student = strings.ReplaceAll(student, ",", "")
		students = append(students, student)
	}

	if err := scanner.Err(); err != nil {
		logError(err.Error())
		log.Fatal(err)
	}
	return students
}

// readSubmissions returns a slice of all filenames from submissions directory
func readSubmissions() []string {
	var submissions []string
	files, err := os.ReadDir("../resources/submissions")
	if err != nil {
		logError(err.Error())
		log.Fatal(err)
	}

	for _, file := range files {
		submissions = append(submissions, file.Name())
	}
	return submissions
}

// copyFile copies the contents of the file named src to the file named
// by dst. The file will be created if it does not already exist. If the
// destination file exists, all it's contents will be replaced by the contents
// of the source file.
func copyFile(src, dst string) {
	in, err := os.Open(src)
	if err != nil {
		logError(err.Error())
		log.Fatal(err)
	}
	defer in.Close()
	out, err := os.Create(dst)
	if err != nil {
		logError(err.Error())
		log.Fatal(err)
	}
	defer func() {
		cerr := out.Close()
		if err == nil {
			err = cerr
		}
	}()
	if _, err = io.Copy(out, in); err != nil {
		logError(err.Error())
		log.Fatal(err)
	}
	err = out.Sync()
}

// recursiveZipSubmissions zips the output student submission files
func recursiveZipSubmissions() {
	pathToZip := "../output/submissions/"
	destinationPath := "../output/submissions.7z"

	destinationFile, err := os.Create(destinationPath)
	if err != nil {
		logError(err.Error())
		log.Fatal(err)
	}
	myZip := zip.NewWriter(destinationFile)
	err = filepath.Walk(pathToZip, func(filePath string, info os.FileInfo, err error) error {
		if info.IsDir() {
			return nil
		}
		if err != nil {
			logError(err.Error())
			log.Fatal(err)
		}
		relPath := strings.TrimPrefix(filePath, filepath.Dir(pathToZip))
		zipFile, err := myZip.Create(relPath)
		if err != nil {
			logError(err.Error())
			log.Fatal(err)
		}
		fsFile, err := os.Open(filePath)
		if err != nil {
			logError(err.Error())
			log.Fatal(err)
		}
		_, err = io.Copy(zipFile, fsFile)
		if err != nil {
			logError(err.Error())
			log.Fatal(err)
		}
		return nil
	})
	if err != nil {
		logError(err.Error())
		log.Fatal(err)
	}
	err = myZip.Close()
	if err != nil {
		logError(err.Error())
		log.Fatal(err)
	}
}

// execute finds the intersection of the wanted student submissions
// it then copies those files to the "../output/submissions" directory
// where it creates a directory of the student name and places the completed
// assignment.
func execute(assignment string) {

	makeDir("../output/submissions")

	var students []string = readStudents()
	var submissions []string = readSubmissions()

	group := 1
	//naive and complicated way to do this, fix later
	for _, student := range students {
		for _, submission := range submissions {
			studentName := strings.Split(submission, "_")[0]
			if studentName == student {
				extension := filepath.Ext(submission)
				groupDir := "../output/submissions/" + "Group" + strconv.Itoa(group) + "/"
				studentDir := groupDir + studentName
				makeDir(studentDir)
				copyFile("../resources/submissions/"+submission, studentDir+"/"+studentName+assignment+extension)
				copyFile("../resources/TAComments", studentDir+"/"+studentName+"TAComments")
			}
		}
		if student == "" || student == "\r" {
			group++
		}
	}
	recursiveZipSubmissions()
}
