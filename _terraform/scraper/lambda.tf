data "aws_caller_identity" "current" {
  provider = "aws.us-west-1"
}
data "archive_file" "scraper" {
  type        = "zip"
  source_file = "${path.root}/../scraper/scraper.py"
  output_path = "${path.root}/${local.scraper_lambda_filename}"
}

resource "aws_lambda_function" "scraper" {
  description      = "get FitBark data for Ripley from the API and stash it in DynamoDB"
  filename         = "${local.scraper_lambda_filename}"
  source_code_hash = "${data.archive_file.scraper.output_base64sha256}"
  function_name    = "RipleyFitbark_Scraper"
  role             = "${var.lambda_role_arn}"
  runtime          = "python3.6"
  handler          = "scraper"
  memory_size      = 128
  timeout          = 20

  environment {
    variables = {
      FOO       = "BAR"
    }
  }
}