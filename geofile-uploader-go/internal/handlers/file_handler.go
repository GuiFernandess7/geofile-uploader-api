package handlers

import (
	"fmt"
	"mime/multipart"
	"os/exec"
	"path/filepath"

	fileController "kmlSender/internal/controllers"
	"kmlSender/internal/helpers"

	"github.com/labstack/echo/v4"
	"github.com/sirupsen/logrus"
)

func ReceiveKMLFile(c echo.Context, log *logrus.Logger) (*multipart.FileHeader, error) {
    file, err := c.FormFile("file")
    if err != nil {
        log.Errorf("[ERROR] - Failed to receive file - %v", err)
        return nil, fmt.Errorf("failed to receive file: %w", err)
    }
    return file, nil
}

func ProcessKMLFile(c echo.Context, file *multipart.FileHeader, log *logrus.Logger) (string, error) {
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

func ConvertKMLToGeoJSON(kmlPath string, geojsonPath string) error {
    cmd := exec.Command("C:\\OSGeo4W\\bin\\ogr2ogr.exe", "-f", "GeoJSON", geojsonPath, kmlPath)
    out, err := cmd.CombinedOutput()
    if err != nil {
        return fmt.Errorf("Error converting KML to geojson: %v\nOutput: %s", err, string(out))
    }
    return nil
}

func UploadGeoJSONToBucket(c echo.Context, filePath string, log *logrus.Logger) error {
    filename := filepath.Base(filePath)

    log.Infof("[INFO] - Sending file [%s] to GCP Bucket...", filename)

    currentFile, err := helpers.OpenLocalFile(filePath)
    if err != nil {
        log.Errorf("[ERROR] - Could not read local file %s: %v", filename, err)
        return fmt.Errorf("failed to read local file: %w", err)
    }
    defer currentFile.Close()

    fileManager := fileController.FController{}
    err = fileManager.StartUpload(currentFile, filePath, filename)
    if err != nil {
        log.Errorf("[ERROR] - Upload of file %s failed: %v", filename, err)
        return fmt.Errorf("failed to upload file: %w", err)
    }

    log.Infof("[%s] - File uploaded successfully!", filename)
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