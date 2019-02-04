provider "aws" {
  region = "us-west-2"
  version = "~> 1.57"
  profile = "ripley_api"
}

provider "archive" {
  version = "1.1"
}

data "aws_caller_identity" "current" {
  provider = "aws"
}

resource "aws_api_gateway_account" "settings" {
  cloudwatch_role_arn = "${aws_iam_role.apigw_cloudwatch.arn}"
}