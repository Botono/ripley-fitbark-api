resource "aws_cognito_user_pool" "pool" {
  name = "ripley-api-user-pool"

  admin_create_user_config = {
      allow_admin_create_user_only = true
  }

  password_policy = {
      minimum_length    = 8
      require_lowercase = true
      require_uppercase = true
      require_numbers   = true
  }
}