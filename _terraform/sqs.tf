resource "aws_sqs_queue" "google_sheets" {
  name                       = "google-sheets-data-queue"
  max_message_size           = 262144
  visibility_timeout_seconds = 10
}

