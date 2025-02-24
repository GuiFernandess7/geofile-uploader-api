package routes

import (
	"fmt"
	"net/http"

	fileController "kmlSender/internal/controllers"
	customMiddleware "kmlSender/internal/middleware"
	"kmlSender/internal/models"
	"kmlSender/internal/utils"

	"github.com/labstack/echo/v4"
	echoMiddleware "github.com/labstack/echo/v4/middleware"
	"github.com/sirupsen/logrus"
)

func RegisterRoutes(router *echo.Echo, log *logrus.Logger) {
    router.Use(echoMiddleware.Recover())

    router.GET("/health-check", func(c echo.Context) error {
        log.Info("[HEALTH-CHECK] - Request received on root endpoint - OK.")
        return c.JSON(http.StatusOK, models.GenericResponse{
            Status:  http.StatusOK,
            Message: "Service is up and running.",
        })
    })

    router.POST("/upload-kml-file", uploadKMLFile(log), customMiddleware.FirebaseAuthMiddleware)
}

func uploadKMLFile(log *logrus.Logger) echo.HandlerFunc {
	return func(c echo.Context) error {
		log.Info("[BEGIN] - Request received on root endpoint - OK.")

		// 1. Receive file
		file, err := c.FormFile("file")
		if err != nil {
			log.Errorf("[ERROR] - File NOT received: %v", err)
			return c.JSON(http.StatusBadRequest, models.FileResponse{
				Status:  http.StatusBadRequest,
				Message: "No file uploaded",
				Filename: nil,
			})
		}

		log.Infof("[UPLOAD] - Received file: %s", file.Filename)

		// 2. Process file
		fileManager := fileController.FController{File: file}
		err = fileManager.DownloadFile(".kml", "tmp")
		if err != nil {
			log.Errorf("[ERROR] - File %s not processed: %v", file.Filename, err)
			return c.JSON(http.StatusInternalServerError, models.FileResponse{
				Status:  http.StatusInternalServerError,
				Message: err.Error(),
				Filename: nil,
			})
		}
		log.Infof("[DOWNLOAD] - File %s downloaded successfully", file.Filename)

		// 3. Read file
		currentFilePath := fmt.Sprintf("tmp/%s", file.Filename)
		currentFile, err := utils.OpenLocalFile(currentFilePath)
		if err != nil {
			log.Errorf("[ERROR] - Local File %s not readed: %v", file.Filename, err)
			utils.DeleteFile(currentFilePath)
			return c.JSON(http.StatusInternalServerError, models.FileResponse{
				Status:  http.StatusInternalServerError,
				Message: err.Error(),
				Filename: nil,
			})
		}
		log.Infof("[READ] - File %s readed successfully", file.Filename)

		// 5. Delete file
		defer func() {
			if currentFile != nil {
				currentFile.Close()
				log.Infof("[OK] - File %s closed", file.Filename)
			}
			err := utils.DeleteFile(currentFilePath)
			if err != nil {
				log.Errorf("[ERROR] - Failed to delete file %s: %v", currentFilePath, err)
			} else {
				log.Infof("[OK] - File %s deleted", currentFilePath)
			}
		}()

		// 4. Upload file
		log.Infof("[INFO] - Sending File [%s] to GCP Bucket... ", file.Filename)
		err = fileManager.UploadFileToBucket(currentFile, currentFilePath, file.Filename)
		if err != nil {
			log.Errorf("[ERROR] - Local File %s not sent: %v", file.Filename, err)
			return c.JSON(http.StatusInternalServerError, models.FileResponse{
				Status:  http.StatusInternalServerError,
				Message: err.Error(),
				Filename: nil,
			})
		}

		log.Infof("[END] - File %s sent successfully", file.Filename)
		return c.JSON(http.StatusOK, models.FileResponse{
			Status:  http.StatusOK,
			Message: "File uploaded successfully",
			Filename: &file.Filename,
		})
	}
}