package api

import (
	"log"
	"time"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/service/s3"
)

const (
	waterStartAmount = 3000
	waterBowlWeight  = 1595
)

func getS3Object(bucket string, key string, buffer *aws.WriteAtBuffer) error {
	defer logElapsedTime(time.Now(), "getS3Object()")
	_, err := s3Downloader.Download(buffer,
		&s3.GetObjectInput{
			Bucket: aws.String(bucket),
			Key:    aws.String(key),
		})

	return err
}

func logElapsedTime(start time.Time, name string) {
	elapsed := time.Since(start)
	log.Printf("%s took %s", name, elapsed)
}
