module "api" {
  source = "./api"

  lambda_role_arn = aws_iam_role.lambda_role.arn
  kms_key_arn     = aws_kms_key.secrets_key.arn
}

