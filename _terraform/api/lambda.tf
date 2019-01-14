data "aws_caller_identity" "current" {
  provider = "aws"
}

data "archive_file" "api" {
  type        = "zip"
  source_dir = "${path.root}/../api_build"
  output_path = "${path.root}/lambda_builds/${local.api_lambda_filename}"
}

resource "aws_lambda_function" "api" {
  description      = "API build with Flask"
  filename         = "${local.api_lambda_filename}"
  source_code_hash = "${data.archive_file.api.output_base64sha256}"
  function_name    = "RipleyFitbark_API"
  role             = "${var.lambda_role_arn}"
  runtime          = "python3.6"
  handler          = "api.handler"
  kms_key_arn      = "${var.kms_key_arn}"
  memory_size      = 128
  timeout          = 30

  environment {
    variables = {
      FOO       = "BAR"
    }
  }
}

resource "aws_cloudwatch_log_group" "api" {
  name              = "/aws/lambda/${aws_lambda_function.api.function_name}"
  retention_in_days = 14
}
