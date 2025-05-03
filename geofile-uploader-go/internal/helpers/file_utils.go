package helpers

import (
	"crypto/sha1"
	"encoding/hex"
	"fmt"
	"io"
	"mime/multipart"
	"os"
	"path/filepath"
	"strings"
)

func ValidateFileExtension(filename, validExt string) error {
	ext := strings.ToLower(filepath.Ext(filename))
	if ext != validExt {
		return fmt.Errorf("invalid file type. Only %s files are allowed, but got: %s", validExt, ext)
	}
	return nil
}

func CreateDirectory(folder string) error {
	if err := os.MkdirAll(folder, os.ModePerm); err != nil {
		return fmt.Errorf("failed to create directory: %w", err)
	}
	return nil
}

func SetDestinationPath(folder, filename string) (*os.File, error) {
	dstPath := filepath.Join(folder, filename)
	dst, err := os.Create(dstPath)
	if err != nil {
		return nil, fmt.Errorf("failed to create the destination file: %w", err)
	}
	return dst, nil
}

func StoreFile(dst *os.File, src multipart.File) error {
	if _, err := io.Copy(dst, src); err != nil {
		return err
	}
	return nil
}

func OpenFile(file *multipart.FileHeader) (multipart.File, error) {
	return file.Open()
}

func OpenLocalFile(filePath string) (*os.File, error){
	file, err := os.Open(filePath)
	return file, err
}

func DeleteFile(filePath string) error {
	err := os.Remove(filePath)
	if err != nil {
		return fmt.Errorf("failed to delete file %s: %v", filePath, err)
	}
	return nil
}

func HashEmail(email string) (string){
	h := sha1.New()
    h.Write([]byte(email))
    sha1_hash := hex.EncodeToString(h.Sum(nil))
	return sha1_hash
}