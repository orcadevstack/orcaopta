variable "cloud" {
  type = string
}

locals {
  is_aws   = var.cloud == "aws"
  is_azure = var.cloud == "azure"
  is_gcp   = var.cloud == "gcp"
}

module "aws" {
  source = "../../modules/aws-infra"
  count  = local.is_aws ? 1 : 0
}

module "azure" {
  source = "../../modules/azure-infra"
  count  = local.is_azure ? 1 : 0
}

module "gcp" {
  source = "../../modules/gcp-infra"
  count  = local.is_gcp ? 1 : 0
}

module "kube" {
  source = "../../modules/kube"
}
