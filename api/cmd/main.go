package main

import (
	"context"
	"log"

	ripleyapi "github.com/Botono/ripley-fitbark-api/api"

	"github.com/aws/aws-lambda-go/events"
	"github.com/aws/aws-lambda-go/lambda"
	ginadapter "github.com/awslabs/aws-lambda-go-api-proxy/gin"
)

var apiAdapter *ginadapter.GinLambda

func handler(ctx context.Context, req events.APIGatewayProxyRequest) (events.APIGatewayProxyResponse, error) {
	return apiAdapter.ProxyWithContext(ctx, req)
}

func main() {
	// If no name is provided in the HTTP request body, throw an error
	log.Println("API CMD MAIN")
	apiAdapter = ginadapter.New(ripleyapi.NewAPI())
	lambda.Start(handler)
}
