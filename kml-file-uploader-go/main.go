package main

import (
	"kmlSender/internal/routes"

	"github.com/labstack/echo/v4"
	"github.com/sirupsen/logrus"
)

func main() {
	var log = logrus.New()
	log.SetFormatter(&logrus.TextFormatter{
		TimestampFormat: "2006-01-02 15:04:05",
		FullTimestamp:   true,
	})

	router := echo.New()
	routes.RegisterRoutes(router, log)
	router.Start(":8000")
}
