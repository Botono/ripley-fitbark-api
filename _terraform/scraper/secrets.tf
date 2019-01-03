resource "aws_kms_key" "secrets_key" {
    description = "RipleyFitBark_Scraper_key"
    deletion_window_in_days = 10
}
