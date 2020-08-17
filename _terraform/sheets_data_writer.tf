module "sheets_data_writer" {
  source = "./sheets_data_writer"

  lambda_role_arn             = aws_iam_role.lambda_role.arn
  kms_key_arn                 = aws_kms_key.secrets_key.arn
  google_sheets_sqs_queue_arn = aws_sqs_queue.google_sheets.arn
}

