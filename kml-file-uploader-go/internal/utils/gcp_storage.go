package utils

import (
	"context"
	"errors"
	"fmt"
	"io"
	"os"

	"cloud.google.com/go/storage"
	"google.golang.org/api/option"
)

type GCPClient struct {
	bucketName string
}

func (gcp *GCPClient) createClient(ctx context.Context, serviceAccCreds string) (*storage.Client, error) {
	var client *storage.Client
	var err error

	if serviceAccCreds != "" {
		client, err = storage.NewClient(ctx, option.WithCredentialsFile(serviceAccCreds))
	} else {
		client, err = storage.NewClient(ctx)
	}

	if err != nil {
		return nil, fmt.Errorf("failed to create client: %w", err)
	}
	return client, nil
}


func (gcp *GCPClient) SetBucket() error {
	bucketName := os.Getenv("bucket_name")
	if bucketName == "" {
		return errors.New("bucket_name is not set in environment variables")
	}

	gcp.bucketName = bucketName
	return nil
}


func (gcp *GCPClient) Upload(file *os.File, filePath string, objectName string) error {
	serviceAccCreds := os.Getenv("GOOGLE_APPLICATION_CREDENTIALS")
	ctx := context.Background()
	client, err := gcp.createClient(ctx, serviceAccCreds)
	if err != nil {
		return err
	}
	defer client.Close()

	bucket := client.Bucket(gcp.bucketName)

	defer file.Close()
	writer := bucket.Object(objectName).NewWriter(ctx)
	defer writer.Close()

	_, err = io.Copy(writer, file)
	if err != nil {
		return fmt.Errorf("failed to copy file to bucket: %w", err)
	}

	if err := writer.Close(); err != nil {
		return fmt.Errorf("failed to close writer: %w", err)
	}

	fmt.Printf("File %s sent successfully to bucket!\n", objectName)
	return nil
}
