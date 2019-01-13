# {"date": "2018-12-30 17:00:00", "activity_value": 402, "min_play": 0, "min_active": 32, "min_rest": 28, "distance_in_miles": 0.05, "kcalories": 30.0, "activity_goal": 23100},

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