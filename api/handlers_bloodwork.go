package api

import (
	"context"
	"log"
	"net/http"
	"time"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/service/dynamodb"
	"github.com/aws/aws-sdk-go/service/dynamodb/dynamodbattribute"
	"github.com/gin-gonic/gin"
)

const (
	tableBloodwork = "Ripley_Bloodwork"
)

func getBloodwork(c *gin.Context) {
	defer logElapsedTime(time.Now(), "getBloodwork()")
	log.Println("GET BLOODWORK DATA")

	bloodworkRecords, err := getBloodworkRecords()

	if err != nil {
		log.Println("ERROR: Failure getting Bloodwork DB Records: ", err.Error())
		c.JSON(http.StatusInternalServerError, errorInternalServer)
		return
	}

	// Create response map
	responseData := make(map[string]bloodworkRecord)

	for _, record := range bloodworkRecords {
		responseData[record.Date] = record
	}

	c.JSON(http.StatusOK, responseData)
}

func getBloodworkLabels(c *gin.Context) {
	labels := []bloodworkLabel{
		{
			Name:  "WBC",
			Lower: 4,
			Upper: 15.5,
		},
		{
			Name:  "RBC",
			Lower: 4.8,
			Upper: 9.3,
		},
		{
			Name:  "HGB",
			Lower: 12.1,
			Upper: 20.3,
		},
		{
			Name:  "HCT",
			Lower: 36,
			Upper: 60,
		},
		{
			Name:  "MCV",
			Lower: 58,
			Upper: 79,
		},
		{
			Name:  "MCH",
			Lower: 19,
			Upper: 28,
		},
		{
			Name:  "MCHC",
			Lower: 30,
			Upper: 38,
		},
		{
			Name:  "Plaelet Count",
			Lower: 170,
			Upper: 400,
		},
		{
			Name:  "Neutrophils %",
			Lower: 60,
			Upper: 77,
		},
		{
			Name:  "Bands",
			Lower: 0,
			Upper: 3,
		},
		{
			Name:  "Lymphocytes %",
			Lower: 12,
			Upper: 30,
		},
		{
			Name:  "Monocytes %",
			Lower: 3,
			Upper: 10,
		},
		{
			Name:  "Eosinophils %",
			Lower: 2,
			Upper: 10,
		},
		{
			Name:  "Basophils %",
			Lower: 0,
			Upper: 1,
		},
		{
			Name:  "Abs Neutrophils",
			Lower: 2060,
			Upper: 10600,
		},
		{
			Name:  "Abs Lymphocytes",
			Lower: 690,
			Upper: 4500,
		},
		{
			Name:  "Abs Monocytes",
			Lower: 0,
			Upper: 840,
		},
		{
			Name:  "Abs Eosinophils",
			Lower: 0,
			Upper: 1200,
		},
		{
			Name:  "Abs Basophils",
			Lower: 0,
			Upper: 150,
		},
	}

	c.JSON(http.StatusOK, labels)
}

func getBloodworkRecords() ([]bloodworkRecord, error) {
	defer logElapsedTime(time.Now(), "getBloodworkRecords()")
	input := dynamodb.ScanInput{
		TableName: aws.String(tableBloodwork),
	}

	bloodworkRecords := []bloodworkRecord{}

	var unmarshalErr error

	ctx, cancel := context.WithTimeout(context.Background(), time.Millisecond*timeoutActivityScan)
	defer cancel()

	err := db.ScanPagesWithContext(ctx, &input, func(scanRecords *dynamodb.ScanOutput, lastPage bool) bool {
		pageItems := []bloodworkRecord{}
		err := dynamodbattribute.UnmarshalListOfMaps(scanRecords.Items, &pageItems)
		if err != nil {
			unmarshalErr = err
			return false
		}

		bloodworkRecords = append(bloodworkRecords, pageItems...)
		return true
	})

	if unmarshalErr != nil {
		log.Println("ERROR: Failed to unmarshal Daily Dynamo items to interface: ", unmarshalErr.Error())
		return nil, unmarshalErr
	}

	return bloodworkRecords, err
}
