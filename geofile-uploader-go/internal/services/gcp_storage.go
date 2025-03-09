package services

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
	Client 	   *storage.Client
}

func (gcp *GCPClient) CreateClient(ctx context.Context, serviceAccCreds string) error {
	var client *storage.Client
	var err error

	if serviceAccCreds != "" {
		client, err = storage.NewClient(ctx, option.WithCredentialsFile(serviceAccCreds))
	} else {
		client, err = storage.NewClient(ctx)
	}

	if err != nil {
		return fmt.Errorf("failed to create client: %w", err)
	}

	gcp.Client = client
	return nil
}


func (gcp *GCPClient) SetBucket() error {
	bucketName := os.Getenv("bucket_name")
	if bucketName == "" {
		return errors.New("bucket_name is not set in environment variables")
	}

	gcp.bucketName = bucketName
	return nil
}

/* func (gcp *GCPClient) ObjectExists(client *storage.Client, fileName string, ctx context.Context) (bool, error) {
    blob := client.Bucket(gcp.bucketName).Object(fileName)
    _, err := blob.Attrs(ctx)
    if err == storage.ErrObjectNotExist {
        return false, nil

    } else if err != nil {
        log.Printf("Error checking existence of object %s: %v", fileName, err)
        return false, fmt.Errorf("error checking existence of object %s: %w", fileName, err)
    }
    return true, nil
} */

func (gcp *GCPClient) ObjectExists(client *storage.Client, fileName string, ctx context.Context) (bool, error) {
    blob := client.Bucket(gcp.bucketName).Object(fileName)
    _, err := blob.Attrs(ctx)
    if errors.Is(err, storage.ErrObjectNotExist) {
        return false, nil
    } else if err != nil {
        return false, fmt.Errorf("error checking existence of object %s: %w", fileName, err)
    }
    return true, nil
}

func (gcp *GCPClient) Upload(client storage.Client, file *os.File, filePath string, objectName string) error {
	ctx := context.Background()
	defer client.Close()

	bucket := client.Bucket(gcp.bucketName)

	defer file.Close()
	writer := bucket.Object(objectName).NewWriter(ctx)
	defer writer.Close()

	_, err := io.Copy(writer, file)
	if err != nil {
		return fmt.Errorf("failed to copy file to bucket: %w", err)
	}

	if err := writer.Close(); err != nil {
		return fmt.Errorf("failed to close writer: %w", err)
	}

	fmt.Printf("File %s sent successfully to bucket!\n", objectName)
	return nil
}
