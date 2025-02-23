package fileController

import (
	"fmt"
	"kmlSender/internal/utils"
	"mime/multipart"
	"os"
)

type FController struct {
	File *multipart.FileHeader
}

func (fc *FController) ProcessFile(validExt, tmpFolder string) error {
	err := utils.ValidateFileExtension(fc.File.Filename, validExt)
	if err != nil {
		return fmt.Errorf("invalid file extension: %w", err)
	}

	src, err := utils.OpenFile(fc.File)
	if err != nil {
		return fmt.Errorf("failed to open file: %w", err)
	}
	defer src.Close()

	err = utils.CreateDirectory(tmpFolder)
	if err != nil {
		return fmt.Errorf("failed to create directory: %w", err)
	}

	dst, err := utils.SetDestinationPath(tmpFolder, fc.File.Filename)
	if err != nil {
		return fmt.Errorf("failed to create destination file: %w", err)
	}
	defer dst.Close()

	err = utils.StoreFile(dst, src)
	if err != nil {
		return fmt.Errorf("failed to save the file: %w", err)
	}

	return nil
}

func (fc *FController) UploadFileToBucket(fileObj *os.File, filePath string, destFileName string) error {
	gcp := &utils.GCPClient{}

	if err := gcp.SetBucket(); err != nil {
		return fmt.Errorf("Bucket error: %w", err)
	}

	if err := gcp.Upload(fileObj, filePath, destFileName); err != nil {
		return fmt.Errorf("Upload error: %w", err)
	}
	return nil
}