data "aws_caller_identity" "current" {
  provider = "aws"
}



data "archive_file" "scraper" {
  type        = "zip"
  source_dir = "${path.root}/../scraper_build"
  output_path = "${path.root}/${local.scraper_lambda_filename}"
}

resource "aws_lambda_function" "scraper" {
  description      = "get FitBark data for Ripley from the API and stash it in DynamoDB"
  filename         = "${local.scraper_lambda_filename}"
  source_code_hash = "${data.archive_file.scraper.output_base64sha256}"
  function_name    = "RipleyFitbark_Scraper"
  role             = "${var.lambda_role_arn}"
  runtime          = "python3.6"
  handler          = "scraper.handler"
  kms_key_arn      = "${aws_kms_key.secrets_key.arn}"
  memory_size      = 128
  timeout          = 20

  environment {
    variables = {
      FOO       = "BAR"
    }
  }
}

resource "aws_cloudwatch_log_group" "scraper" {
  name              = "/aws/lambda/${aws_lambda_function.scraper.function_name}"
  retention_in_days = 14
}

resource "aws_cloudwatch_event_rule" "nine_am" {
  name = "nine-am"
  description = "fires at 9AM UTC every day"
  schedule_expression = "cron(0 9 * * ? *)"
}

resource "aws_cloudwatch_event_target" "trigger_scraper_lambda" {
  rule = "${aws_cloudwatch_event_rule.nine_am.name}"
  arn = "${aws_lambda_function.scraper.arn}"
}
