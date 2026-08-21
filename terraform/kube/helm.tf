terraform {
  required_providers {
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.11"
    }
  }
}

provider "helm" {
  kubernetes {
    host                   = var.kube_host
    client_certificate     = file(var.client_cert)
    client_key             = file(var.client_key)
    cluster_ca_certificate = file(var.cluster_ca)
  }
}

resource "helm_release" "orcaopta_api" {
  name       = "orcaopta-api"
  chart      = "./helm/orcaopta-api"   # local chart
  namespace  = "orcaopta"
  create_namespace = true

  set {
    name  = "image.repository"
    value = var.api_image_repo
  }

  set {
    name  = "image.tag"
    value = var.api_image_tag
  }
}
