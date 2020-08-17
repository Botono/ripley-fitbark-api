data "aws_caller_identity" "current" {
  provider = aws
}

data "archive_file" "sheets_data_writer" {
  type        = "zip"
  source_dir  = "${path.root}/../_lambda_builds/sheets_data_writer_build"
  output_path = "${path.root}/${local.sheets_data_writer_lambda_filename}"
}

resource "aws_lambda_function" "sheets_data_writer" {
  description      = "get FitBark data for Ripley from the API and stash it in DynamoDB"
  filename         = local.sheets_data_writer_lambda_filename
  source_code_hash = data.archive_file.sheets_data_writer.output_base64sha256
  function_name    = "RipleyAPI_SheetsDataWriter"
  role             = var.lambda_role_arn
  runtime          = "python3.6"
  handler          = "sheets_data_writer.handler"
  kms_key_arn      = var.kms_key_arn
  memory_size      = 128
  timeout          = 10
}

resource "aws_cloudwatch_log_group" "sheets_data_writer" {
  name              = "/aws/lambda/${aws_lambda_function.sheets_data_writer.function_name}"
  retention_in_days = 14
}

resource "aws_lambda_event_source_mapping" "sheets_data_writer_trigger" {
  event_source_arn = var.google_sheets_sqs_queue_arn
  function_name    = aws_lambda_function.sheets_data_writer.arn
  enabled          = true
  batch_size       = 1
}

