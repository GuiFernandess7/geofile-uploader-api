package routes

import (
	"net/http"

	fileController "kmlSender/internal/controllers"
	"kmlSender/internal/models"

	"github.com/labstack/echo/v4"
	"github.com/sirupsen/logrus"
)

func RegisterRoutes(router *echo.Echo, log *logrus.Logger) {
	router.GET("/health-check", func(c echo.Context) error {
		log.Info("[HEALTH-CHECK] - Request received on root endpoint - OK.")
		return c.JSON(http.StatusOK, models.GenericResponse{
			Status:  http.StatusOK,
			Message: "Service is up and running",
		})
	})

	router.POST("/upload-kml-file", uploadKMLFile(log))
}

func uploadKMLFile(log *logrus.Logger) echo.HandlerFunc {
	return func(c echo.Context) error {
		file, err := c.FormFile("file")
		if err != nil {
			log.Errorf("[ERROR] - File %s NOT received: %v", file.Filename, err)
			return c.JSON(http.StatusBadRequest, models.FileResponse{
				Status:  http.StatusBadRequest,
				Message: "No file uploaded",
				Filename: nil,
			})
		}
		log.Infof("[OK] - File %s received successfully.", file.Filename)

		fileManager := fileController.FController{File: file}

		err = fileManager.ProcessFile(".kml", "tmp")
		if err != nil {
			log.Errorf("[ERROR] - File %s not processed: %v", file.Filename, err)
			return c.JSON(http.StatusInternalServerError, models.FileResponse{
				Status:  http.StatusInternalServerError,
				Message: err.Error(),
				Filename: nil,
			})
		}
		log.Infof("[OK] - File %s processed successfully.", file.Filename)

		return c.JSON(http.StatusOK, models.FileResponse{
			Status:  http.StatusOK,
			Message: "File uploaded and saved successfully",
			Filename: &file.Filename,
		})
	}

}
