package main

import (
	"log"

	"github.com/Botono/ripley-fitbark-api/scraper"

	"github.com/aws/aws-lambda-go/lambda"
)

func handler(event scraper.ScrapeEvent) {
	log.Println("Starting Scraper")
	s := scraper.NewScraper(event)
	s.Scrape()
	log.Println("DONE")
}

func main() {
	lambda.Start(handler)
}
