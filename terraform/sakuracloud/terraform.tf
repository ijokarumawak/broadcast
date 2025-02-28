terraform {
  backend "remote" {
    hostname     = "app.terraform.io"
    organization = "kusama"
    workspaces {
      name = "sakuracloud"
    }
  }
  required_providers {
    sakuracloud = {
      source  = "sacloud/sakuracloud"
      version = "~> 2.18.0"
    }
    github = {
      source  = "integrations/github"
      version = "~> 5.0"
    }
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.0"
    }
  }
}
provider "sakuracloud" {
}
provider "github" {}

provider "aws" {
}