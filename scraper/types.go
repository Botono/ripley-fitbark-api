package scraper

import (
	"strings"

	"github.com/aws/aws-sdk-go/service/dynamodb/dynamodbiface"
)

// ScrapeEvent represents the event data sent from AWS
type ScrapeEvent struct {
	From       string
	To         string
	Resolution string
}

type config struct {
	event           ScrapeEvent
	db              dynamodbiface.DynamoDBAPI
	fitBarkURL      string
	apiToken        string
	slug            string
	responseStructs []*interface{}
}

type Scraper struct {
	config *config
}

type fitBarkRequest struct {
	ActivitySeries fitBarActivitySeries `json:"activity_series"`
}

type fitBarActivitySeries struct {
	Slug       string `json:"slug"`
	From       string `json:"from"`
	To         string `json:"to"`
	Resolution string `json:"resolution"`
}

type fitBarkResponseHourly struct {
	ActivitySeries struct {
		Slug    string             `json:"slug"`
		Records []fitBarkHourEntry `json:"records"`
	} `json:"activity_series"`
}

func (f *fitBarkResponseHourly) formatDates() {
	records := f.ActivitySeries.Records
	for i := 0; i < len(records); i++ {
		dateSlice := strings.Split(records[i].Date, " ")
		records[i].Date = dateSlice[0]
		records[i].Time = dateSlice[1]
	}

	f.ActivitySeries.Records = records
}

type fitBarkResponseDaily struct {
	ActivitySeries struct {
		Slug    string            `json:"slug"`
		Records []fitBarkDayEntry `json:"records"`
	} `json:"activity_series"`
}

func NewFitBarkResponse(resolution string) interface{} {
	if resolution == hourly {
		return &fitBarkResponseHourly{}
	} else {
		return &fitBarkResponseDaily{}
	}
}

type fitBarkDayEntry struct {
	Date          string `json:"date"`
	ActivityValue uint32 `json:"activity_value"`
	MinPlay       uint32 `json:"min_play"`
	MinActive     uint32 `json:"min_active"`
	MinRest       uint32 `json:"min_rest"`
	DailyTarget   uint32 `json:"daily_target"`
	HasTrophy     uint32 `json:"has_trophy"`
}

type fitBarkHourEntry struct {
	Date          string `json:"date"`
	Time          string `json:"time"`
	ActivityValue uint32 `json:"activity_value"`
	MinPlay       uint32 `json:"min_play"`
	MinActive     uint32 `json:"min_active"`
	MinRest       uint32 `json:"min_rest"`
}
