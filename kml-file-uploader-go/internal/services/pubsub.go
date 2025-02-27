package services

import (
	"context"
	"fmt"
	"os"

	"cloud.google.com/go/pubsub"
	log "github.com/sirupsen/logrus"
)

var (
	projectID = os.Getenv("project_id")
	topicID = os.Getenv("pubsub-topic")
)

func PublishMessage(filename string) error {
	ctx := context.Background()
	client, err := pubsub.NewClient(ctx, projectID)
	if err != nil {
		log.Fatalf("Error creating pubsub client: %v", err)
		return err
	}
	defer client.Close()

	topic := client.Topic(topicID)

	result := topic.Publish(ctx, &pubsub.Message{
		Data: []byte(filename),
	})

	id, err := result.Get(ctx)
	if err != nil {
		log.Fatalf("Erro publishing message: %v", err)
		return err
	}

	fmt.Printf("Filename '%s' published successfully! ID: %s\n", filename, id)
	return nil
}
