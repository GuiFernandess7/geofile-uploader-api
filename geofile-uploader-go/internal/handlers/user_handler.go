package handlers

import (
	"github.com/labstack/echo/v4"
	"github.com/sirupsen/logrus"
)

func ReceiveUserEmail(c echo.Context, log *logrus.Logger) string {
    email, ok := c.Get("email").(string)
    if !ok {
        log.Warn("Email not found or not a string")
        return ""
    }
    return email
}