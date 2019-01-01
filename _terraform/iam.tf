data "aws_caller_identity" "current" {
  provider = "aws.us-west-1"
}

resource "aws_iam_role" "lambda_invoke" {
  provider = "aws.us-west-1"
  name     = "ripley-fitbark-lambda-invoke"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}