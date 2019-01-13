terraform {
  backend "s3" {
    bucket  = "ripleyapi-terraform-state"
    key     = "production/terraform.tfstate"
    region  = "us-west-1"
    profile = "ripley_api"
  }
}