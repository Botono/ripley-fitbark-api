resource "aws_iam_role" "lambda_role" {
  provider = "aws"
  name     = "ripley-fitbark-lambda"

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

resource "aws_iam_role" "apigw_cloudwatch" {
  name = "api_gateway_cloudwatch_global"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "",
      "Effect": "Allow",
      "Principal": {
        "Service": "apigateway.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy" "apigw_cloudwatch" {
  name = "default"
  role = "${aws_iam_role.apigw_cloudwatch.id}"

  policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:DescribeLogGroups",
                "logs:DescribeLogStreams",
                "logs:PutLogEvents",
                "logs:GetLogEvents",
                "logs:FilterLogEvents"
            ],
            "Resource": "*"
        }
    ]
}
EOF
}

resource "aws_iam_policy" "lambda_logging_policy" {
  provider = "aws"
  name = "lambda_logging"

  policy = <<EOF
{
   "Version":"2012-10-17",
   "Statement":[
      {
         "Effect":"Allow",
         "Action":[
            "logs:CreateLogStream",
            "logs:PutLogEvents"
         ],
         "Resource": "arn:aws:logs:us-west-1:${data.aws_caller_identity.current.account_id}:*"
      }
   ]
}
EOF
}

resource "aws_iam_policy" "lambda_secrets_policy" {
  provider = "aws"
  name = "lambda_secrets"

  policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": [
          "secretsmanager:GetSecretValue"
        ],
        "Resource": "arn:aws:secretsmanager:*:${data.aws_caller_identity.current.account_id}:*:*"
      },
      {
        "Effect": "Allow",
        "Action": [
          "kms:*"
        ],
        "Resource": "*"
      }
    ]
}
EOF
}

resource "aws_iam_policy" "lambda_dynamodb_policy" {
  provider = "aws"
  name = "lambda_dynamodb"

  policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:DeleteItem",
                "dynamodb:GetItem",
                "dynamodb:PutItem",
                "dynamodb:Scan",
                "dynamodb:Query",
                "dynamodb:UpdateItem"
            ],
            "Resource": [
              "arn:aws:dynamodb:us-west-1:${data.aws_caller_identity.current.account_id}:table/${aws_dynamodb_table.fitbark_daily.name}",
              "arn:aws:dynamodb:us-west-1:${data.aws_caller_identity.current.account_id}:table/${aws_dynamodb_table.fitbark_hourly.name}"
            ]
        }
    ]
}
EOF
}


resource "aws_iam_role_policy_attachment" "lambda_logging_attach" {
  role = "${aws_iam_role.lambda_role.name}"
  policy_arn = "${aws_iam_policy.lambda_logging_policy.arn}"
}

resource "aws_iam_role_policy_attachment" "lambda_secrets_attach" {
  role = "${aws_iam_role.lambda_role.name}"
  policy_arn = "${aws_iam_policy.lambda_secrets_policy.arn}"
}

resource "aws_iam_role_policy_attachment" "lambda_dynamodb_attach" {
  role = "${aws_iam_role.lambda_role.name}"
  policy_arn = "${aws_iam_policy.lambda_dynamodb_policy.arn}"
}
