package main

import (
	"fmt"
	"log"
	"os"

	"kmlSender/internal/middleware"
	"kmlSender/internal/routes"

	"github.com/joho/godotenv"
	"github.com/labstack/echo/v4"
	"github.com/sirupsen/logrus"
)

func setUpEnv(local bool) error {
	if local {
		err := godotenv.Load()
		if err != nil {
			return fmt.Errorf("error loading .env file: %w", err)
		}
		log.Println("Successfully loaded environment variables from .env file.")
	}

	bucketName := os.Getenv("bucket_name")
	if bucketName == "" {
		err := fmt.Errorf("bucket_name is not set in environment variables")
		return err
	}

	log.Printf("Using bucket: %s", bucketName)
	return nil
}

func main() {
	var log = logrus.New()
	log.SetFormatter(&logrus.TextFormatter{
		TimestampFormat: "2006-01-02 15:04:05",
		FullTimestamp:   true,
	})

	local := true
	err := setUpEnv(local)
	if err != nil {
		log.Errorf("Error setting up env variables: %v", err)
		return
	}

	err = middleware.InitFirebase(".creds/firebase.json", log)
	if err != nil {
		log.Errorf("Firebase error: %v", err)
		return
	}

	router := echo.New()
	routes.RegisterRoutes(router, log)
	if err := router.Start(":8000"); err != nil {
		log.Fatalf("Error starting server: %v", err)
	}
}
