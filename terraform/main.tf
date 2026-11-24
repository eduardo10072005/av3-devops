terraform {
  required_version = ">= 1.6"

  required_providers {
    aiven = {
      source  = "aiven/aiven"
      version = "~> 4.0"
    }
  }
}

provider "aiven" {
  api_token = var.aiven_api_token
}

# Removemos o bloco do aiven_project. Vamos usar o que já existe.

# Serviço PostgreSQL gerenciado (plano gratuito)
resource "aiven_pg" "db" {
  project      = var.aiven_project
  cloud_name   = var.cloud_name
  plan         = var.pg_plan
  service_name = var.service_name
}

# Database da aplicação dentro do serviço
resource "aiven_pg_database" "app" {
  project       = var.aiven_project
  service_name  = aiven_pg.db.service_name
  database_name = var.database_name
}

# Usuário adicional
resource "aiven_pg_user" "extra" {
  project      = var.aiven_project
  service_name = aiven_pg.db.service_name
  username     = var.db_username
}
