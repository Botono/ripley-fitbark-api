locals {
  scraper_lambda_filename = "scraper.zip"
}

variable "lambda_role_arn" {
  type="string"
  description="the ARN of the Lambda IAM Role"
  
}
