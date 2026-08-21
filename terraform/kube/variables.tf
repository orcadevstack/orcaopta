variable "kube_host" {
  type = string
}

variable "client_cert" {
  type = string
}

variable "client_key" {
  type = string
}

variable "cluster_ca" {
  type = string
}

variable "api_image" {
  type    = string
  default = "orcaopta-api:latest"
}

variable "api_image_repo" {
  type    = string
  default = "orcaopta-api"
}

variable "api_image_tag" {
  type    = string
  default = "latest"
}
