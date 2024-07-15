terraform {
  backend "pg" {
    conn_str = "postgres://db/terraform"
  }
  required_providers {
    keycloak = {
      source  = "mrparkers/keycloak"
      version = "4.4.0"
    }
  }
}

# REST API credentials and URL
variable "keycloak_client_id" {
  type    = string
  default = "admin-cli"
}
variable "keycloak_user" {
  type    = string
  default = "admin"
}
variable "keycloak_password" {
  type      = string
  sensitive = true
}
variable "keycloak_url" {
  type    = string
  default = "http://keycloak:8080/auth"
}

# Application client variables
variable "app_client_id" {
  type    = string
  default = "app"
}

variable "valid_redirect_uris" {
  type = list(string)
}

# Keycloak realm user for testing
variable "create_user" {
  type    = bool
  default = false
}

variable "user_username" {
  type = string
  default = "bruce"
}

variable "user_password" {
  type      = string
  sensitive = true
}

variable "user_first_name" {
  type = string
  default = "Bruce"
}

variable "user_last_name" {
  type = string
  default = "Lee"
}

variable "user_email" {
  type = string
  default = "bruce@kung.fu"
}

# Providers
provider "keycloak" {
  client_id = var.keycloak_client_id
  username  = var.keycloak_user
  password  = var.keycloak_password
  url       = var.keycloak_url
}

# Application realm
resource "keycloak_realm" "app" {
  realm = "app"
}

# Application client
resource "keycloak_openid_client" "openid_client" {
  realm_id              = keycloak_realm.app.id
  client_id             = var.app_client_id
  access_type           = "PUBLIC"
  standard_flow_enabled = true
  implicit_flow_enabled = true
  direct_access_grants_enabled = true

  valid_redirect_uris = var.valid_redirect_uris

  # Allow the same values (except for "*") as those set in valid_redirect_uris
  web_origins = ["+"]
  #full_scope_allowed =
}

resource "keycloak_user" "bruce" {
  count    = var.create_user ? 1 : 0
  realm_id = keycloak_realm.app.id
  username = var.user_username
  enabled  = true

  email      = var.user_email
  first_name = var.user_first_name
  last_name  = var.user_last_name

  initial_password {
    value     = var.user_password
    temporary = false
  }
}
