resource "aws_dynamodb_table" "fitbark_hourly" {
  name           = "RipleyFitbark_Activity_Hourly"
  read_capacity  = 10
  write_capacity = 5
  hash_key       = "date"
  range_key      = "time"

  attribute {
    name = "date"
    type = "S"
  }

  attribute {
    name = "time"
    type = "S"
  }

  point_in_time_recovery {
    enabled = true
  }
}

resource "aws_dynamodb_table" "fitbark_daily" {
  name           = "RipleyFitbark_Activity_Daily"
  read_capacity  = 10
  write_capacity = 5
  hash_key       = "date"

  attribute {
    name = "date"
    type = "S"
  }

  point_in_time_recovery {
    enabled = true
  }
}

resource "aws_dynamodb_table" "ripley_water" {
  name           = "Ripley_Water"
  read_capacity  = 10
  write_capacity = 5
  hash_key       = "date"

  attribute {
    name = "date"
    type = "S"
  }

  point_in_time_recovery {
    enabled = true
  }
}

resource "aws_dynamodb_table" "ripley_changelog" {
  name           = "Ripley_Changelog"
  read_capacity  = 10
  write_capacity = 5
  hash_key       = "messageHash"
  range_key      = "date"

  attribute {
    name = "date"
    type = "S"
  }

  attribute {
    name = "messageHash"
    type = "S"
  }

  point_in_time_recovery {
    enabled = true
  }
}

resource "aws_dynamodb_table" "ripley_bloodwork" {
  name           = "Ripley_Bloodwork"
  read_capacity  = 10
  write_capacity = 5
  hash_key       = "date"

  attribute {
    name = "date"
    type = "S"
  }

  point_in_time_recovery {
    enabled = true
  }
}

