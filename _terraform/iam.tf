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

resource "aws_iam_policy" "lambda_logging_policy" {
  provider = "aws"
  
  policy = <<EOF
{
   "Version":"2012-10-17",
   "Statement":[
      {
         "Effect":"Allow",
         "Action":"logs:CreateLogGroup",
         "Resource":"arn:aws:logs:us-west-1:${data.aws_caller_identity.current.account_id}:*"
      },
      {
         "Effect":"Allow",
         "Action":[
            "logs:CreateLogStream",
            "logs:PutLogEvents"
         ],
         "Resource":[
            "arn:aws:logs:us-west-1:${data.aws_caller_identity.current.account_id}:log-group:[[logGroups]]:*"
         ]
      }
   ]
}
EOF
}

resource "aws_iam_policy" "lambda_secrets_policy" {
  provider = "aws"

  policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": {
        "Effect": "Allow",
        "Action": [
          "secretsmanager:GetSecretValue",
          "kms:*"
        ],
        "Resource": [
          "arn:aws:secretsmanager:*:${data.aws_caller_identity.current.account_id}:*:*",
          "arn:aws:kms:*:${data.aws_caller_identity.current.account_id}:*"
        ]
    }
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
