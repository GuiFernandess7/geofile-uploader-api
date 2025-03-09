package fileController

import (
	"context"
	"fmt"
	"kmlSender/internal/helpers"
	"kmlSender/internal/services"
	"mime/multipart"
	"os"
)

type FController struct {
	File *multipart.FileHeader
}

func (fc *FController) DownloadFile(validExt, tmpFolder string) error {
	err := helpers.ValidateFileExtension(fc.File.Filename, validExt)
	if err != nil {
		return fmt.Errorf("invalid file extension - %w", err)
	}

	src, err := helpers.OpenFile(fc.File)
	if err != nil {
		return fmt.Errorf("failed to open file - %w", err)
	}
	defer src.Close()

	err = helpers.CreateDirectory(tmpFolder)
	if err != nil {
		return fmt.Errorf("failed to create directory - %w", err)
	}

	dst, err := helpers.SetDestinationPath(tmpFolder, fc.File.Filename)
	if err != nil {
		return fmt.Errorf("failed to create destination file - %w", err)
	}
	defer dst.Close()

	err = helpers.StoreFile(dst, src)
	if err != nil {
		return fmt.Errorf("failed to save the file - %w", err)
	}

	return nil
}

func (fc *FController) StartUpload(fileObj *os.File, filePath string, destFileName string) error {
    gcp := &services.GCPClient{}
    serviceAccCreds := os.Getenv("GOOGLE_APPLICATION_CREDENTIALS")
    ctx := context.Background()

    if err := gcp.CreateClient(ctx, serviceAccCreds); err != nil {
        return fmt.Errorf("failed to create GCP client: %w", err)
    }
    defer gcp.Client.Close()

    if err := gcp.SetBucket(); err != nil {
        return fmt.Errorf("Bucket error - %w", err)
    }

    objExists, err := gcp.ObjectExists(gcp.Client, destFileName, ctx)
    if err != nil {
        return fmt.Errorf("error checking object existence: %w", err)
    }
    if objExists {
        return fmt.Errorf("Object %s already exists in bucket", destFileName)
    }
    if err := gcp.Upload(*gcp.Client, fileObj, filePath, destFileName); err != nil {
        return fmt.Errorf("Upload error - %w", err)
    }
    return nil
}


func (fc *FController) PublishFilename(filename string) error {
	err := services.PublishMessage(filename)
	if err != nil {
		return err
	}
	return nil
}