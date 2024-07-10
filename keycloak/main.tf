terraform {
  backend "pg" {
    conn_str = "postgres://db/terraform"
  }
  required_providers {
    keycloak = {
      source = "mrparkers/keycloak"
      version = "4.4.0"
    }
  }
}

variable "keycloak_client_id" {
  type        = string
  default     = "admin-cli"
}
variable "keycloak_user" {
  type        = string
  default     = "admin"
}
variable "keycloak_password" {
  type        = string
  sensitive   = true
}
variable "keycloak_url" {
  type        = string
  default     = "http://keycloak:8080"
}

provider "keycloak" {
    client_id     = var.keycloak_client_id
    username      = var.keycloak_user
    password      = var.keycloak_password
    url           = var.keycloak_url
}

resource "keycloak_realm" "realm" {
  realm = "app"
}
