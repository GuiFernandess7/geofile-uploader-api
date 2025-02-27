package handlers

import (
	"fmt"
	"mime/multipart"
	"net/http"

	fileController "kmlSender/internal/controllers"
	"kmlSender/internal/helpers"
	"kmlSender/internal/models"

	"github.com/labstack/echo/v4"
	"github.com/sirupsen/logrus"
)

func ReceiveFile(c echo.Context, log *logrus.Logger) (*multipart.FileHeader, error) {
	file, err := c.FormFile("file")
	if err != nil {
		log.Errorf("[ERROR] - Failed to receive file - %v", err)
		return nil, c.JSON(http.StatusBadRequest, models.FileResponse{
			Status:  http.StatusBadRequest,
			Message: "Failed to receive file: " + err.Error(),
		})
	}
	return file, nil
}

func ProcessFile(c echo.Context, file *multipart.FileHeader, log *logrus.Logger) (string, error) {
	fileManager := fileController.FController{File: file}
	err := fileManager.DownloadFile(".kml", "tmp")
	if err != nil {
		log.Errorf("[ERROR] - File %s not processed: %v", file.Filename, err)
		return "", c.JSON(http.StatusInternalServerError, models.FileResponse{
			Status:  http.StatusInternalServerError,
			Message: err.Error(),
		})
	}

	filePath := fmt.Sprintf("tmp/%s", file.Filename)
	log.Infof("[DOWNLOAD] - File %s downloaded successfully", file.Filename)
	return filePath, nil
}

func UploadToBucket(file *multipart.FileHeader, filePath string, log *logrus.Logger) error {
	log.Infof("[INFO] - Sending File [%s] to GCP Bucket...", file.Filename)
	return nil

	currentFile, err := helpers.OpenLocalFile(filePath)
	if err != nil {
		log.Errorf("[ERROR] - Local File %s not read: %v", file.Filename, err)
		return fmt.Errorf("file not read: %w", err)
	}
	defer currentFile.Close()

	fileManager := fileController.FController{File: file}
	err = fileManager.UploadFileToBucket(currentFile, filePath, file.Filename)
	if err != nil {
		log.Errorf("[ERROR] - Local File %s not sent: %v", file.Filename, err)
		return fmt.Errorf("file not read: %w", err)
	}

	return nil
}

func PublishToPubSub(filename string, log *logrus.Logger) error {
	fileManager := fileController.FController{}
	err := fileManager.PublishFilename(filename)
	if err != nil {
		log.Errorf("[ERROR] - Publish message failed for file: %v - %v", filename, err)
		return fmt.Errorf("file not read: %w", err)
	}
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