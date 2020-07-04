locals {
  api_lambda_filename = "apilambda.zip"
}

variable "lambda_role_arn" {
  type="string"
  description="the ARN of the Lambda IAM Role"
}

variable "kms_key_arn" {
  type="string"
  description="the ARN of the Secrets KMS Key"
}
