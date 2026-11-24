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

# Cria o projeto dentro da organização existente
resource "aiven_project" "project" {
  project   = var.aiven_project
  parent_id = "org5f7d471a8f0"
}

# Serviço PostgreSQL gerenciado
resource "aiven_pg" "db" {
  project      = aiven_project.project.project
  cloud_name   = var.cloud_name
  plan         = var.pg_plan
  service_name = var.service_name
}

# Database da aplicação dentro do serviço
resource "aiven_pg_database" "app" {
  project       = aiven_project.project.project
  service_name  = aiven_pg.db.service_name
  database_name = var.database_name
}

# Usuário adicional (prática de gestão de acesso)
resource "aiven_pg_user" "extra" {
  project      = aiven_project.project.project
  service_name = aiven_pg.db.service_name
  username     = var.db_username
}
