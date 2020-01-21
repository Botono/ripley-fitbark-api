package main

import (
	"context"

	ripleyapi "ripley-fitbark-api/api"

	"github.com/aws/aws-lambda-go/events"
	"github.com/aws/aws-lambda-go/lambda"
	"github.com/awslabs/aws-lambda-go-api-proxy/gin"
)

var apiAdapter *ginadapter.GinLambda

func handler(ctx context.Context, req events.APIGatewayProxyRequest) (events.APIGatewayProxyResponse, error) {
	// If no name is provided in the HTTP request body, throw an error
	apiAdapter = ginadapter.New(ripleyapi.NewAPI())
	return apiAdapter.ProxyWithContext(ctx, req)
}

func main() {

	lambda.Start(handler)
}
