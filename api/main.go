package api

import (
	"log"
	"regexp"
	"time"

	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/dynamodb"
	"github.com/aws/aws-sdk-go/service/s3/s3manager"
	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
)

var (
	awsSession   *session.Session
	s3Downloader *s3manager.Downloader
	s3Uploader   *s3manager.Uploader
	db           *dynamodb.DynamoDB
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

	// CORS middleware
	r.Use(cors.New(cors.Config{
		AllowOriginFunc:  isOriginValid,
		AllowMethods:     []string{"PUT", "PATCH", "POST", "DELETE", "GET", "OPTIONS"},
		AllowHeaders:     []string{"Origin", "Content-Type", "x-api-key"},
		ExposeHeaders:    []string{"Content-Length"},
		AllowCredentials: true,
		MaxAge:           12 * time.Hour,
	}))

	// ROUTES
	r.GET("/water", getWaterCollection)
	r.POST("/water", postWater)
	r.GET("/fitbark/activity", getFitbarkActivity)
	r.GET("/changelog", getChangelog)
	r.GET("/bloodwork", getBloodwork)
	r.GET("/bloodwork/labels", getBloodworkLabels)

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

	log.Printf("Origin %s is not allowed!", origin)

	return false
}

func setupAWS() {
	log.Println("Setting up AWS APIs...")
	awsSession = session.Must(session.NewSession())
	s3Downloader = s3manager.NewDownloader(awsSession)
	s3Uploader = s3manager.NewUploader(awsSession)
	db = dynamodb.New(awsSession)
}
