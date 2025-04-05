package handlers

import (
	"github.com/labstack/echo/v4"
	"github.com/sirupsen/logrus"
)

type EmailBody struct {
    Email string `json:"email"`
}

func ReceiveUserEmail(c echo.Context, log *logrus.Logger) string {
    var body EmailBody
    if err := c.Bind(&body); err != nil {
        log.Warn("Failed to bind request body")
        return ""
    }

    if body.Email == "" {
        log.Warn("Email is empty in request body")
        return ""
    }

    return body.Email
}