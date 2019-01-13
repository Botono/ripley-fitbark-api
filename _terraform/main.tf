provider "aws" {
  region = "us-west-1"
  version = "~> 1.55"
  profile = "ripley_api"
}

provider "archive" {
  version = "1.1"
}

data "aws_caller_identity" "current" {
  provider = "aws"
}