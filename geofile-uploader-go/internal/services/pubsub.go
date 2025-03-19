package services

import (
	"context"
	"os"

	"cloud.google.com/go/pubsub"
	log "github.com/sirupsen/logrus"
	"google.golang.org/api/option"
)

func PublishMessage(jsonData []byte) error {
	projectID := os.Getenv("PROJECT_ID")
	topicID := os.Getenv("TOPIC_ID")
	credentialsFile := os.Getenv("GOOGLE_APPLICATION_CREDENTIALS")
	ctx := context.Background()

	client, err := pubsub.NewClient(ctx, projectID, option.WithCredentialsFile(credentialsFile))
	if err != nil {
		log.Fatalf("Error creating pubsub client: %v", err)
		return err
	}
	defer client.Close()

	topic := client.Topic(topicID)

	result := topic.Publish(ctx, &pubsub.Message{
        Data: jsonData,
    })

	_, err = result.Get(ctx)
	if err != nil {
		log.Fatalf("Erro publishing message: %v", err)
		return err
	}
	return nil
}
