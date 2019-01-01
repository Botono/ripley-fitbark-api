provider "aws" {
  alias  = "us-west-1"
  region = "us-west-1"
  version = "~> 1.51"
}

provider "archive" {
  version = "1.1"
}