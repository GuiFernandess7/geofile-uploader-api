package middleware

import (
	"context"
	"fmt"
	"net/http"
	"strings"

	"kmlSender/internal/models"

	firebase "firebase.google.com/go"
	"firebase.google.com/go/auth"
	"github.com/labstack/echo/v4"
	"github.com/sirupsen/logrus"
	"google.golang.org/api/option"
)

var AuthClient *auth.Client

func InitFirebase(credsPath string, log *logrus.Logger) error {
    opt := option.WithCredentialsFile(credsPath)
    log.Info("[AUTH] - Initializing Firebase Authentication...")

    app, err := firebase.NewApp(context.Background(), nil, opt)
    if err != nil {
        log.Errorf("[AUTH] - error initializing app: %v\n", err)
        return err
    }

    AuthClient, err = app.Auth(context.Background())
    if err != nil {
        log.Errorf("[AUTH] - Error getting firebase client: %v\n", err)
        return err
    }
    log.Info("[OK] - Firebase initialized successfully!")
    return nil
}

func FirebaseAuthMiddleware(next echo.HandlerFunc) echo.HandlerFunc {
    return func(c echo.Context) error {
        authHeader := c.Request().Header.Get("Authorization")
        if authHeader == "" {
            return c.JSON(http.StatusUnauthorized, models.GenericResponse{
                Status:  http.StatusUnauthorized,
                Message: "Token not found.",
            })
        }

        token := strings.TrimPrefix(authHeader, "Bearer ")
        decodedToken, err := AuthClient.VerifyIDToken(context.Background(), token)
        if err != nil {
            fmt.Println(err)
            return c.JSON(http.StatusUnauthorized, models.GenericResponse{
                Status:  http.StatusUnauthorized,
                Message: "Invalid token.",
            })
        }

        c.Set("uid", decodedToken.UID)
        return next(c)
    }
}
