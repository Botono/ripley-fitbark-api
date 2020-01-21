package scraper

import (
	"bytes"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"time"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/dynamodb"
	"github.com/aws/aws-sdk-go/service/dynamodb/dynamodbattribute"
	"github.com/aws/aws-sdk-go/service/dynamodb/dynamodbiface"
	"github.com/aws/aws-sdk-go/service/secretsmanager"
	"github.com/json-iterator/go"
)

const (
	hourly = "HOURLY"
	daily  = "DAILY"
)

var (
	json        = jsoniter.ConfigCompatibleWithStandardLibrary
	resolutions = []string{
		hourly,
		daily,
	}
	tables = map[string]string{
		hourly: "RipleyFitbark_Activity_Hourly",
		daily:  "RipleyFitbark_Activity_Daily",
	}
)

// NewScraper returns a pointer to a new Scraper
func NewScraper(event ScrapeEvent) *Scraper {
	mySession := session.Must(session.NewSession())
	secretsMgr := secretsmanager.New(mySession)

	apiToken, err := secretsMgr.GetSecretValue(&secretsmanager.GetSecretValueInput{
		SecretId: aws.String("RipleyFitbark_api_token"),
	})

	if err != nil {
		log.Println("ERROR: Could not fetch API Token from Secrets")
		return &Scraper{}
	}

	slug, err := secretsMgr.GetSecretValue(&secretsmanager.GetSecretValueInput{
		SecretId: aws.String("RipleyFitbark_ripley_slug"),
	})

	if err != nil {
		log.Println("ERROR: Could not fetch Slug from Secrets")
		return &Scraper{}
	}

	return &Scraper{
		config: &config{
			event:      event,
			db:         dynamodb.New(mySession),
			fitBarkURL: "https://app.fitbark.com/api/v2/activity_series",
			apiToken:   *apiToken.SecretString,
			slug:       *slug.SecretString,
		},
	}
}

func elapsedTime(eventName string, startTime time.Time) {
	log.Printf("%s took %s", eventName, time.Since(startTime))
}

// Scrape queries the FitBark API and saves it to DynamoDB and S3 (for now)
func (s *Scraper) Scrape() {
	defer elapsedTime("Scrape()", time.Now())
	log.Println("Beginning scrape...")

	respBytes, err := s.getFitBarkData(hourly)

	if err != nil {
		log.Fatalln("ERROR: ", err)
	}

	hourlyResponse := &fitBarkResponseHourly{}
	respErr := json.Unmarshal(respBytes, hourlyResponse)

	if respErr != nil {
		log.Fatalln("ERROR: Failed unmarshalling FitBark Hourly response: ", err)
	}

	log.Println(fmt.Sprintf("Hourly data retrieved successfully. Records: %d", len(hourlyResponse.ActivitySeries.Records)))

	hourlyResponse.formatDates()

	hourlyResponse.save(s.config.db)

	respBytes, err = s.getFitBarkData(daily)

	if err != nil {
		log.Fatalln("ERROR: ", err)
	}

	dailyResponse := &fitBarkResponseDaily{}
	respErr = json.Unmarshal(respBytes, dailyResponse)

	if respErr != nil {
		log.Fatalln("ERROR: Failed unmarshalling FitBark Daily response: ", err)
	}

	log.Println(fmt.Sprintf("Daily data retrieved successfully. Records: %d", len(dailyResponse.ActivitySeries.Records)))

	dailyResponse.save(s.config.db)

}

func (h *fitBarkResponseHourly) save(db dynamodbiface.DynamoDBAPI) {
	defer elapsedTime("fitBarkResponseHourly.save()", time.Now())
	for _, value := range h.ActivitySeries.Records {
		av, _ := dynamodbattribute.MarshalMap(value)
		putItem := &dynamodb.PutItemInput{
			Item:      av,
			TableName: aws.String(tables[hourly]),
		}
		_, err := db.PutItem(putItem)
		if err != nil {
			log.Println("ERROR: Failed to save Hourly data to DB: ", value.Date, value.Time)
		}
	}
}

func (d *fitBarkResponseDaily) save(db dynamodbiface.DynamoDBAPI) {
	defer elapsedTime("fitBarkResponseDaily.save()", time.Now())
	for _, value := range d.ActivitySeries.Records {
		av, _ := dynamodbattribute.MarshalMap(value)
		putItem := &dynamodb.PutItemInput{
			Item:      av,
			TableName: aws.String(tables[daily]),
		}
		_, err := db.PutItem(putItem)
		if err != nil {
			log.Println("ERROR: Failed to save Daily data to DB: ", value.Date)
		}
	}
}

func (s *Scraper) getFitBarkData(resolution string) ([]byte, error) {
	defer elapsedTime("getFitBarkData()", time.Now())
	// Set default range
	now := time.Now()
	location, err := time.LoadLocation("America/Los_Angeles")
	if err != nil {
		log.Fatal(err)
	}

	// You gotta Add a negative to subtract a duration ugh
	startDate := now.Add(time.Hour * 24 * 7 * -1).In(location).Format("2006-01-02")
	endDate := now.Add(time.Hour * 24 * 1 * -1).In(location).Format("2006-01-02")

	requestBody := fitBarkRequest{
		ActivitySeries: fitBarActivitySeries{
			From:       startDate,
			To:         endDate,
			Resolution: resolution,
			Slug:       s.config.slug,
		},
	}

	jsonBody, _ := json.Marshal(requestBody)

	log.Println(fmt.Sprintf("Fetching %s data between %s and %s", resolution, startDate, endDate))
	req, err := http.NewRequest("POST", s.config.fitBarkURL, bytes.NewBuffer(jsonBody))
	if err != nil {
		return nil, err
	}
	req.Header.Set("Authorization", fmt.Sprintf("Bearer %s", s.config.apiToken))
	req.Header.Set("Content-Type", "application/json")

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("FitBark API Request failed: %s", err.Error())
	}
	defer resp.Body.Close()

	respBytes, err := ioutil.ReadAll(resp.Body)

	if err != nil {
		log.Fatal()
		return nil, fmt.Errorf("Failure reading response into bytes: %s", err.Error())
	}

	if resp.StatusCode >= 400 {
		return nil, fmt.Errorf("FitBark API Request failed with status: %s", resp.Status)
	}

	return respBytes, nil
}
