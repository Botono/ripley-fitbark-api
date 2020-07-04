package api

import (
	"log"
	"regexp"

	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/s3/s3manager"
	"github.com/gin-gonic/gin"
)

var (
	awsSession   *session.Session
	s3Downloader *s3manager.Downloader
)

// NewAPI returns a new instance of the Gin API
func NewAPI() *gin.Engine {
	log.Printf("Ripley API starting up...")
	// Creates a router without any middleware by default
	r := gin.New()

	// Global middleware
	// Logger middleware will write the logs to gin.DefaultWriter even if you set with GIN_MODE=release.
	// By default gin.DefaultWriter = os.Stdout
	r.Use(gin.Logger())

	// Recovery middleware recovers from any panics and writes a 500 if there was one.
	r.Use(gin.Recovery())

	// // CORS middleware
	// r.Use(cors.New(cors.Config{
	// 	AllowOriginFunc:  isOriginValid,
	// 	AllowMethods:     []string{"PUT", "PATCH", "POST", "DELETE", "GET", "OPTIONS"},
	// 	AllowHeaders:     []string{"Origin"},
	// 	ExposeHeaders:    []string{"Content-Length"},
	// 	AllowCredentials: true,
	// 	MaxAge:           12 * time.Hour,
	// }))

	// Simple group: v1
	v1 := r.Group("/v1")
	{
		v1.GET("/water", getWaterCollection)
	}

	setupAWS()

	log.Println("New API setup complete!")

	return r
}

func isOriginValid(origin string) bool {
	validOrigins := []*regexp.Regexp{
		regexp.MustCompile("http://localhost:3000"),
		regexp.MustCompile("^(https?://(?:.+\\.)?ripley\\.dog(?::\\d{1,5})?)$"),
		regexp.MustCompile("^(https?://(?:.+\\.)?botono\\.com(?::\\d{1,5})?)$"),
	}

	for _, re := range validOrigins {
		if re.FindString(origin) != "" {
			return true
		}
	}

	return false
}

func setupAWS() {
	log.Println("Setting up AWS APIs...")
	awsSession = session.Must(session.NewSession())
	s3Downloader = s3manager.NewDownloader(awsSession)
}
