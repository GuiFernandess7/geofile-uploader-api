package routes

import (
	"kmlSender/internal/handlers"
	"kmlSender/internal/helpers"
	"kmlSender/internal/models"
	customMiddleware "kmlSender/internal/services"
	"net/http"
	"strings"

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
        hashedEmail := helpers.HashEmail(user_email)
        user_email = ""

        log.Infof("Email received - %s", hashedEmail)
        file, err := handlers.ReceiveKMLFile(c, log)
        if err != nil {
            return c.JSON(http.StatusBadRequest, models.FileResponse{
                Status:  http.StatusBadRequest,
                Message: err.Error(),
                Filename: nil,
            })
        }
        log.Infof("[{%s}] - Received file - OK.", file.Filename)

        filePath, err := handlers.ProcessKMLFile(c, file, log)
        if err != nil {
            return c.JSON(http.StatusInternalServerError, models.FileResponse{
                Status:  http.StatusInternalServerError,
                Message: err.Error(),
                Filename: nil,
            })
        }
        log.Infof("[{%s}] - Processing file - OK.", file.Filename)

        log.Infof("[{%s}] - Converting to GeoJson...", file.Filename)
        geojsonPath := strings.TrimSuffix(filePath, ".kml") + ".geojson"
        err = handlers.ConvertKMLToGeoJSON(filePath, geojsonPath)
        if err != nil {
            return c.JSON(http.StatusInternalServerError, models.FileResponse{
                Status:  http.StatusInternalServerError,
                Message: err.Error(),
                Filename: nil,
            })
        }
        log.Infof("[{%s}] - KML Converted successfully.", file.Filename)

        err = handlers.UploadGeoJSONToBucket(c, geojsonPath, log)
        if err != nil {
            return c.JSON(http.StatusInternalServerError, models.FileResponse{
                Status:  http.StatusInternalServerError,
                Message: err.Error(),
                Filename: nil,
            })
        }
        log.Infof("[{%s}] - GeoJSON uploaded successfully.", file.Filename)

        err = handlers.PublishToPubSub(file.Filename, hashedEmail, log)
        if err != nil {
            return c.JSON(http.StatusInternalServerError, models.FileResponse{
                Status:  http.StatusInternalServerError,
                Message: err.Error(),
                Filename: nil,
            })
        }

        handlers.CleanUpFile(filePath, log)
        handlers.CleanUpFile(geojsonPath, log)
        log.Infof("[END] - File %s uploaded, published, and cleaned up successfully", file.Filename)

        return c.JSON(http.StatusAccepted, models.FileResponse{
            Status:   http.StatusAccepted,
            Message:  "File upload started.",
            Filename: &file.Filename,
        })
    }
}
