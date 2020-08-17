package api

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"strings"
	"time"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/service/dynamodb"
	"github.com/aws/aws-sdk-go/service/dynamodb/dynamodbattribute"
	"github.com/aws/aws-sdk-go/service/dynamodb/expression"
	"github.com/gin-gonic/gin"
)

const (
	tableActivity       = "RipleyFitbark_Activity_%s"
	resolutionHourly    = "hourly"
	resolutionDaily     = "daily"
	timeoutActivityScan = 20000
)

// NumberOfDays is the only supported query method at first
func getFitbarkActivity(c *gin.Context) {
	defer logElapsedTime(time.Now(), "getFitbarkActivity()")
	log.Println("GET FITBARK ACTIVITY")

	requestData := fitbarkActivityRequest{}

	log.Println("QUERY PARAMS: ", c.Query("numberOfDays"), c.Query("resolution"))

	if err := c.ShouldBindQuery(&requestData); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	now := time.Now()
	startDate := now.AddDate(0, 0, requestData.NumberOfDays*-1)

	log.Printf("Resolution: %s, Number of Days: %d, Start Date: %s", requestData.Resolution, requestData.NumberOfDays, startDate.Format("2006-01-02"))

	switch requestData.Resolution {
	case resolutionDaily:
		log.Println("Scanning for Daily records")
		activityRecords, err := getDailyActivityRecords(startDate)

		if err != nil {
			log.Println("ERROR: Failure getting Daily Activity DB Records: ", err.Error())
			c.JSON(http.StatusInternalServerError, errorInternalServer)
			return
		}

		// Create response map
		responseData := make(map[string]fitbarkActivityRecordDaily)

		for _, record := range activityRecords {
			responseData[record.Date] = record
		}

		c.JSON(http.StatusOK, responseData)
	case resolutionHourly:
		log.Println("Scanning for Hourly records")
		activityRecords, err := getHourlyActivityRecords(startDate)

		if err != nil {
			log.Println("ERROR: Failure getting Hourly Activity DB Records: ", err.Error())
			c.JSON(http.StatusInternalServerError, errorInternalServer)
			return
		}

		// Create response map
		responseData := make(map[string][]fitbarkActivityRecordHourly)

		for _, record := range activityRecords {
			responseData[record.Date] = append(responseData[record.Date], record)
		}

		c.JSON(http.StatusOK, responseData)
	}
}

func getDailyActivityRecords(startDate time.Time) ([]fitbarkActivityRecordDaily, error) {
	defer logElapsedTime(time.Now(), "getDailyActivityRecords()")
	ctx, cancel := context.WithTimeout(context.Background(), time.Millisecond*timeoutActivityScan)
	defer cancel()

	filter := expression.Name("date").GreaterThanEqual(expression.Value(startDate.Format("2006-01-02")))
	expr, _ := expression.NewBuilder().WithFilter(filter).Build()

	input := dynamodb.ScanInput{
		TableName:                 aws.String(fmt.Sprintf(tableActivity, strings.Title(resolutionDaily))),
		FilterExpression:          expr.Filter(),
		ExpressionAttributeNames:  expr.Names(),
		ExpressionAttributeValues: expr.Values(),
	}

	activityRecords := []fitbarkActivityRecordDaily{}

	var unmarshalErr error

	err := db.ScanPagesWithContext(ctx, &input, func(scanRecords *dynamodb.ScanOutput, lastPage bool) bool {
		pageItems := []fitbarkActivityRecordDaily{}
		err := dynamodbattribute.UnmarshalListOfMaps(scanRecords.Items, &pageItems)
		if err != nil {
			unmarshalErr = err
			return false
		}

		activityRecords = append(activityRecords, pageItems...)
		return true
	})

	if unmarshalErr != nil {
		log.Println("ERROR: Failed to unmarshal Daily Dynamo items to interface: ", unmarshalErr.Error())
		return nil, unmarshalErr
	}

	return activityRecords, err
}

func getHourlyActivityRecords(startDate time.Time) ([]fitbarkActivityRecordHourly, error) {
	defer logElapsedTime(time.Now(), "getHourlyActivityRecords()")

	ctx, cancel := context.WithTimeout(context.Background(), time.Millisecond*timeoutActivityScan)
	defer cancel()

	filter := expression.Name("date").GreaterThanEqual(expression.Value(startDate.Format("2006-01-02")))
	expr, _ := expression.NewBuilder().WithFilter(filter).Build()

	input := dynamodb.ScanInput{
		TableName:                 aws.String(fmt.Sprintf(tableActivity, strings.Title(resolutionHourly))),
		FilterExpression:          expr.Filter(),
		ExpressionAttributeNames:  expr.Names(),
		ExpressionAttributeValues: expr.Values(),
	}

	activityRecords := []fitbarkActivityRecordHourly{}

	var unmarshalErr error

	err := db.ScanPagesWithContext(ctx, &input, func(scanRecords *dynamodb.ScanOutput, lastPage bool) bool {
		pageItems := []fitbarkActivityRecordHourly{}
		err := dynamodbattribute.UnmarshalListOfMaps(scanRecords.Items, &pageItems)
		if err != nil {
			unmarshalErr = err
			return false
		}

		activityRecords = append(activityRecords, pageItems...)
		return true
	})

	if unmarshalErr != nil {
		log.Println("ERROR: Failed to unmarshal Hourly Dynamo items to interface: ", unmarshalErr.Error())
		return nil, unmarshalErr
	}

	return activityRecords, err
}
