variable "location" {
  type    = string
  default = "westeurope"
}

variable "admin_password" {
  type      = string
  sensitive = true
}

variable "storage_account_name" {
  type = string
}
