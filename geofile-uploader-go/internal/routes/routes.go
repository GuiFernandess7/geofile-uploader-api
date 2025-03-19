package routes

import (
	"kmlSender/internal/handlers"
	"kmlSender/internal/models"
	customMiddleware "kmlSender/internal/services"
	"net/http"

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

        user_email := handlers.ReceiveUserEmail(c, log)
        file, err := handlers.ReceiveFile(c, log)
        if err != nil {
            return c.JSON(http.StatusBadRequest, models.FileResponse{
                Status:  http.StatusBadRequest,
                Message: err.Error(),
                Filename: nil,
            })
        }
        log.Infof("[{%s}] - Received file - OK.", file.Filename)

        filePath, err := handlers.ProcessFile(c, file, log)
        if err != nil {
            return c.JSON(http.StatusInternalServerError, models.FileResponse{
                Status:  http.StatusInternalServerError,
                Message: err.Error(),
                Filename: nil,
            })
        }
        log.Infof("[{%s}] - Processing file - OK.", file.Filename)

        err = handlers.UploadToBucket(c, file, filePath, log)
        if err != nil {
            return c.JSON(http.StatusInternalServerError, models.FileResponse{
                Status:  http.StatusInternalServerError,
                Message: err.Error(),
                Filename: nil,
            })
        }

        err = handlers.PublishToPubSub(file.Filename, user_email, log)
        if err != nil {
            return c.JSON(http.StatusInternalServerError, models.FileResponse{
                Status:  http.StatusInternalServerError,
                Message: err.Error(),
                Filename: nil,
            })
        }

        handlers.CleanUpFile(filePath, log)
        log.Infof("[END] - File %s uploaded, published, and cleaned up successfully", file.Filename)

        return c.JSON(http.StatusAccepted, models.FileResponse{
            Status:   http.StatusAccepted,
            Message:  "File upload started.",
            Filename: &file.Filename,
        })
    }
}
