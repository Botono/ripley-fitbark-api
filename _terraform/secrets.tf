resource "aws_kms_key" "secrets_key" {
    description = "RipleyFitBark_key"
    deletion_window_in_days = 10
}

resource "aws_kms_alias" "secrets_key" {
  name = "alias/ripleyfitbark_secrets"
  target_key_id = "${aws_kms_key.secrets_key.key_id}"
}


resource "aws_secretsmanager_secret" "fitbark_api_token" {
    name = "RipleyFitbark_api_token"
    kms_key_id = "${aws_kms_key.secrets_key.key_id}"
    recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "fitbark_api_token" {
    secret_id = "${aws_secretsmanager_secret.fitbark_api_token.id}"
    secret_string = "${var.fitbark_api_token}"
}

resource "aws_secretsmanager_secret" "fitbark_ripley_slug" {
    name = "RipleyFitbark_ripley_slug"
    kms_key_id = "${aws_kms_key.secrets_key.key_id}"
    recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "fitbark_ripley_slug" {
    secret_id = "${aws_secretsmanager_secret.fitbark_ripley_slug.id}"
    secret_string = "${var.fitbark_ripley_slug}"
}
