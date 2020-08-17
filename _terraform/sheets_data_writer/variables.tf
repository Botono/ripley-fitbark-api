locals {
  sheets_data_writer_lambda_filename = "sheets_data_writer.zip"
}

variable "lambda_role_arn" {
  type        = string
  description = "the ARN of the Lambda IAM Role"
}

variable "kms_key_arn" {
  type        = string
  description = "the ARN of the Secrets KMS Key"
}

variable "google_sheets_sqs_queue_arn" {
  type        = string
  description = "The ARN of the SQS Queue for Google Forms inputs"
}

