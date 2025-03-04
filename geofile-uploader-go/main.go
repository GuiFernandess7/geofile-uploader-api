package main

import (
	"fmt"
	"os"

	"kmlSender/internal/routes"
	"kmlSender/internal/services"

	"github.com/joho/godotenv"
	"github.com/labstack/echo/v4"
	"github.com/sirupsen/logrus"
)

func setUpEnv(local bool, log *logrus.Logger) error {
    if local {
        err := godotenv.Load()
        if err != nil {
            return fmt.Errorf("error loading .env file: %w", err)
        }
        log.Println("Successfully loaded environment variables from .env file.")
    }

    projectID := os.Getenv("PROJECT_ID")
    log.Printf("Loaded Project ID: %s", projectID)

    if projectID == "" {
        err := fmt.Errorf("PROJECT_ID is not set in environment variables")
        return err
    }
    log.Printf("Using project ID: %s", projectID)

    bucketName := os.Getenv("bucket_name")
    if bucketName == "" {
        err := fmt.Errorf("bucket_name is not set in environment variables")
        return err
    }
    log.Printf("Using bucket: %s", bucketName)

    credentialsFile := os.Getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if credentialsFile == "" {
        err := fmt.Errorf("GOOGLE_APPLICATION_CREDENTIALS is not set in environment variables")
        return err
    }
    log.Printf("Using credentials file: %s", credentialsFile)

    return nil
}

func main() {
	var log = logrus.New()
	log.SetFormatter(&logrus.TextFormatter{
		TimestampFormat: "2006-01-02 15:04:05",
		FullTimestamp:   true,
	})

	local := true
	err := setUpEnv(local, log)
	if err != nil {
		log.Errorf("Error setting up env variables: %v", err)
		return
	}

	err = services.InitFirebase(".creds/firebase.json", log)
	if err != nil {
		log.Errorf("Firebase error: %v", err)
		return
	}

	router := echo.New()
	routes.RegisterRoutes(router, log)
	if err := router.Start(":8090"); err != nil {
		log.Fatalf("Error starting server: %v", err)
	}
}
