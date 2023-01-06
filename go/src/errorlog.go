package main

import (
	"log"
	"os"
)

// logError logs any errors ocurring in the program to "error_logs.txt"
func logError(errorMessage string) {
	f, err := os.OpenFile("../error_logs.txt", os.O_RDWR|os.O_CREATE|os.O_APPEND, 0666)
	if err != nil {
		log.Fatalf("error opening file: %v", err)
	}
	defer f.Close()

	log.SetOutput(f)
	log.Println(errorMessage)
}
