package handlers

import (
	"fmt"
	"mime/multipart"

	fileController "kmlSender/internal/controllers"
	"kmlSender/internal/helpers"

	"github.com/labstack/echo/v4"
	"github.com/sirupsen/logrus"
)

func ReceiveFile(c echo.Context, log *logrus.Logger) (*multipart.FileHeader, error) {
    file, err := c.FormFile("file")
    if err != nil {
        log.Errorf("[ERROR] - Failed to receive file - %v", err)
        return nil, fmt.Errorf("failed to receive file: %w", err)
    }
    return file, nil
}

func ProcessFile(c echo.Context, file *multipart.FileHeader, log *logrus.Logger) (string, error) {
    fileManager := fileController.FController{File: file}
    err := fileManager.DownloadFile(".kml", "tmp")
    if err != nil {
        log.Errorf("[ERROR] - File %s not processed: %v", file.Filename, err)
        return "", fmt.Errorf("failed to process file: %w", err)
    }

    filePath := fmt.Sprintf("tmp/%s", file.Filename)
    log.Infof("[DOWNLOAD] - File %s downloaded successfully", file.Filename)
    return filePath, nil
}

func UploadToBucket(c echo.Context, file *multipart.FileHeader, filePath string, log *logrus.Logger) error {
    log.Infof("[INFO] - Sending File [%s] to GCP Bucket...", file.Filename)

    currentFile, err := helpers.OpenLocalFile(filePath)
    if err != nil {
        log.Errorf("[ERROR] - Local File %s not read: %v", file.Filename, err)
        return fmt.Errorf("failed to read local file: %w", err)
    }
    defer currentFile.Close()

    fileManager := fileController.FController{File: file}
    err = fileManager.StartUpload(currentFile, filePath, file.Filename)
    if err != nil {
        log.Errorf("[ERROR] - File %s not sent: %v", file.Filename, err)
        return fmt.Errorf("failed to upload file: %w", err)
    }

    log.Infof("[%s] - File upload started!", file.Filename)
    return nil
}


func PublishToPubSub(filename string, userEmail string, log *logrus.Logger) error {
    fileManager := fileController.FController{}

    err := fileManager.PublishFileAndEmail(filename, userEmail)
    if err != nil {
        log.Errorf("[ERROR] - Publish message failed for file: %v - %v", filename, err)
        return fmt.Errorf("failed to publish filename %s: %w", filename, err)
    }

    log.Infof("[SUCCESS] - Filename and Email %s emitted successfully!", filename)
    return nil
}

func CleanUpFile(filePath string, log *logrus.Logger) {
	err := helpers.DeleteFile(filePath)
	if err != nil {
		log.Errorf("[ERROR] - Failed to delete file %s: %v", filePath, err)
	} else {
		log.Infof("[OK] - File %s deleted", filePath)
	}
}