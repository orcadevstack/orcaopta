terraform {
  required_version = ">= 1.5"
}

# Load remote backend
# (global/backend.tf handles backend config)

variable "cloud" {
  type    = string
  default = "aws"
}

variable "environment" {
  type    = string
  default = "dev"
}

module "env" {
  source = "./environments/${var.environment}"
  cloud  = var.cloud
}
