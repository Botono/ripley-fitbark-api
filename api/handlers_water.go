package api

import (
	"bytes"
	"encoding/json"
	"log"
	"net/http"
	"time"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/service/s3/s3manager"
	"github.com/gin-gonic/gin"
)

const (
	dataBucket          = "ripley-health-api-data"
	waterDataKey        = "water/data.json"
	waterDataKeyTest    = "water/data_test.json"
	errorInternalServer = "Internal Server Error"
)

func getWaterCollection(c *gin.Context) {
	defer logElapsedTime(time.Now(), "getWaterCollection()")
	log.Println("WATER: GET ALL DATA")
	buff := &aws.WriteAtBuffer{}
	err := getS3Object(dataBucket, waterDataKey, buff)

	if err != nil {
		log.Println("ERROR: Failed to download water data file: ", err.Error())
		c.JSON(http.StatusInternalServerError, errorInternalServer)
		return
	}

	c.Data(http.StatusOK, gin.MIMEJSON, buff.Bytes())
}

func postWater(c *gin.Context) {
	defer logElapsedTime(time.Now(), "postWater()")
	log.Println("WATER: CREATE NEW ENTRY")

	var requestData newWaterRequest
	if err := c.BindJSON(&requestData); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	waterData := make(map[string]waterEntry)

	buff := &aws.WriteAtBuffer{}
	err := getS3Object(dataBucket, waterDataKey, buff)

	if err != nil {
		log.Println("ERROR: Failed to download water data file: ", err.Error())
		c.JSON(http.StatusInternalServerError, errorInternalServer)
		return
	}

	err = json.Unmarshal(buff.Bytes(), &waterData)

	if err != nil {
		log.Println("ERROR: Failed to unmarshal water data JSON bytes: ", err.Error())
		c.JSON(http.StatusInternalServerError, errorInternalServer)
		return
	}

	waterDate := requestData.Date.String()
	newWaterData := waterEntry{}
	newWaterData.Water = requestData.convertWater()
	newWaterData.KibbleEaten = requestData.KibbleEaten
	newWaterData.Notes = requestData.Notes
	waterData[waterDate] = newWaterData

	// UPLOAD TO S3
	waterDataJSON, err := json.Marshal(waterData)

	if err != nil {
		log.Println("ERROR: Failed to marshal waterData map to JSON bytes:", err.Error())
		c.JSON(http.StatusInternalServerError, errorInternalServer)
		return
	}

	uploadBuffer := bytes.NewBuffer(waterDataJSON)

	_, err = s3Uploader.Upload(&s3manager.UploadInput{
		Bucket: aws.String(dataBucket),
		Key:    aws.String(waterDataKey),
		Body:   uploadBuffer,
	})

	if err != nil {
		log.Println("ERROR: Failed to upload water data to S3: ", err.Error())
		c.JSON(http.StatusInternalServerError, errorInternalServer)
		return
	}

	c.JSON(http.StatusOK, waterData)
}
