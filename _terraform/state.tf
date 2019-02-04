terraform {
  backend "s3" {
    bucket  = "ripley.dog-api-terraform-state"
    key     = "production/terraform.tfstate"
    region  = "us-west-2"
    profile = "ripley_api"
  }
}