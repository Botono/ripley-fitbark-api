package api

import (
	"log"
	"net/http"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/service/s3"
	"github.com/gin-gonic/gin"
)

const (
	dataBucket          = "ripley-health-api-data"
	errorInternalServer = "Internal Server Error"
)

func getWaterCollection(c *gin.Context) {
	log.Println("WATER: GET ALL DATA")
	buff := &aws.WriteAtBuffer{}
	_, err := s3Downloader.Download(buff,
		&s3.GetObjectInput{
			Bucket: aws.String(dataBucket),
			Key:    aws.String("water/data.json"),
		})

	if err != nil {
		log.Println("ERROR: Failed to download water data file: ", err.Error())
		c.JSON(http.StatusInternalServerError, errorInternalServer)
		return
	}

	c.JSON(http.StatusOK, buff.Bytes())
}
