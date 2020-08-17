resource "aws_s3_bucket" "api_data" {
  bucket = "ripley-health-api-data"

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        kms_master_key_id = aws_kms_key.secrets_key.arn
        sse_algorithm     = "aws:kms"
      }
    }
  }
}

