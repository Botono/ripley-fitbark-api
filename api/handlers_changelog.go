package api

import (
	"context"
	"log"
	"net/http"
	"sort"
	"time"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/service/dynamodb"
	"github.com/aws/aws-sdk-go/service/dynamodb/dynamodbattribute"
	"github.com/gin-gonic/gin"
)

const (
	tableChangelog = "Ripley_Changelog"
)

func getChangelog(c *gin.Context) {
	defer logElapsedTime(time.Now(), "getChangelog()")
	log.Println("GET CHANGELOG DATA")

	logRecords, err := getChangelogRecords()

	if err != nil {
		log.Println("ERROR: Failure getting Changelog DB Records: ", err.Error())
		c.JSON(http.StatusInternalServerError, errorInternalServer)
		return
	}

	sort.Slice(logRecords, func(i, j int) bool {
		return logRecords[i].Date > logRecords[j].Date
	})

	c.JSON(http.StatusOK, logRecords)
}

func getChangelogRecords() ([]changeLogRecord, error) {
	defer logElapsedTime(time.Now(), "getChangelogRecords()")
	input := dynamodb.ScanInput{
		TableName: aws.String(tableChangelog),
	}

	logRecords := []changeLogRecord{}

	var unmarshalErr error

	ctx, cancel := context.WithTimeout(context.Background(), time.Millisecond*timeoutActivityScan)
	defer cancel()

	err := db.ScanPagesWithContext(ctx, &input, func(scanRecords *dynamodb.ScanOutput, lastPage bool) bool {
		pageItems := []changeLogRecord{}
		err := dynamodbattribute.UnmarshalListOfMaps(scanRecords.Items, &pageItems)
		if err != nil {
			unmarshalErr = err
			return false
		}

		logRecords = append(logRecords, pageItems...)
		return true
	})

	if unmarshalErr != nil {
		log.Println("ERROR: Failed to unmarshal Daily Dynamo items to interface: ", unmarshalErr.Error())
		return nil, unmarshalErr
	}

	return logRecords, err
}
