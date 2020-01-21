package main

import (
	"log"

	"ripley-fitbark-api/scraper"

	"github.com/aws/aws-lambda-go/lambda"
)

func Handler(event scraper.ScrapeEvent) {
	log.Println("Starting Scraper")
	s := scraper.NewScraper(event)
	s.Scrape()
	log.Println("DONE")
}

func main() {
	lambda.Start(Handler)
}
