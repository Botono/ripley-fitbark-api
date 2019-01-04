# {"date": "2018-12-30 17:00:00", "activity_value": 402, "min_play": 0, "min_active": 32, "min_rest": 28, "distance_in_miles": 0.05, "kcalories": 30.0, "activity_goal": 23100},

resource "aws_dynamodb_table" "fitbark-hourly" {
  name           = "RipleyFitbark_Activity_Hourly"
  read_capacity  = 10
  write_capacity = 5
  hash_key       = "Date"
  range_key      = "Time"

  attribute {
    name = "Date"
    type = "S"
  }

  attribute {
    name = "Time"
    type = "S"
  }

  point_in_time_recovery {
      enabled = true
  }

}

resource "aws_dynamodb_table" "fitbark-daily" {
  name           = "RipleyFitbark_Activity_Daily"
  read_capacity  = 10
  write_capacity = 5
  hash_key       = "Date"

  attribute {
    name = "Date"
    type = "S"
  }

  point_in_time_recovery {
      enabled = true
  }

}