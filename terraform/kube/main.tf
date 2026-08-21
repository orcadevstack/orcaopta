terraform {
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.25"
    }
  }
}

provider "kubernetes" {
  host                   = var.kube_host
  client_certificate     = file(var.client_cert)
  client_key             = file(var.client_key)
  cluster_ca_certificate = file(var.cluster_ca)
}

# Namespace
resource "kubernetes_namespace" "orcaopta" {
  metadata {
    name = "orcaopta"
  }
}

# Deployment
resource "kubernetes_deployment" "api" {
  metadata {
    name      = "orcaopta-api"
    namespace = kubernetes_namespace.orcaopta.metadata[0].name
  }

  spec {
    replicas = 1

    selector {
      match_labels = {
        app = "orcaopta-api"
      }
    }

    template {
      metadata {
        labels = {
          app = "orcaopta-api"
        }
      }

      spec {
        container {
          image = var.api_image
          name  = "orcaopta-api"

          port {
            container_port = 8000
          }
        }
      }
    }
  }
}

# Service
resource "kubernetes_service" "api" {
  metadata {
    name      = "orcaopta-api"
    namespace = kubernetes_namespace.orcaopta.metadata[0].name
  }

  spec {
    selector = {
      app = "orcaopta-api"
    }

    port {
      port        = 80
      target_port = 8000
    }

    type = "LoadBalancer"
  }
}

resource "kubernetes_horizontal_pod_autoscaler_v2" "orcaopta_hpa" {
  metadata {
    name      = "orcaopta-api-hpa"
    namespace = kubernetes_namespace.orcaopta.metadata[0].name
  }

  spec {
    scale_target_ref {
      kind       = "Deployment"
      name       = kubernetes_deployment.api.metadata[0].name
      api_version = "apps/v1"
    }

    min_replicas = 1
    max_replicas = 5

    metric {
      type = "Resource"

      resource {
        name = "cpu"

        target {
          type               = "Utilization"
          average_utilization = 60
        }
      }
    }
  }
}

resource "kubernetes_ingress_v1" "orcaopta_ingress" {
  metadata {
    name      = "orcaopta-api-ingress"
    namespace = kubernetes_namespace.orcaopta.metadata[0].name
    annotations = {
      "kubernetes.io/ingress.class" = "nginx"
    }
  }

  spec {
    rule {
      http {
        path {
          path     = "/"
          path_type = "Prefix"

          backend {
            service {
              name = kubernetes_service.api.metadata[0].name

              port {
                number = 80
              }
            }
          }
        }
      }
    }
  }
}

resource "kubernetes_config_map_v1" "orcaopta_config" {
  metadata {
    name      = "orcaopta-config"
    namespace = kubernetes_namespace.orcaopta.metadata[0].name
  }

  data = {
    APP_ENV      = "production"
    LOG_LEVEL    = "info"
    MODEL_PATH   = "/app/models"
  }
}

resource "kubernetes_secret_v1" "orcaopta_secret" {
  metadata {
    name      = "orcaopta-secret"
    namespace = kubernetes_namespace.orcaopta.metadata[0].name
  }

  type = "Opaque"

  data = {
    API_KEY = base64encode("super-secret-key")
  }
}

spec {
  container {
    name  = "orcaopta-api"
    image = var.api_image

    env_from {
      config_map_ref {
        name = kubernetes_config_map_v1.orcaopta_config.metadata[0].name
      }
    }

    env {
      name = "API_KEY"
      value_from {
        secret_key_ref {
          name = kubernetes_secret_v1.orcaopta_secret.metadata[0].name
          key  = "API_KEY"
        }
      }
    }
  }
}
