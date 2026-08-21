terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
  }
}

provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "rg" {
  name     = "rg-orcaopta"
  location = var.location
}

# VNet
resource "azurerm_virtual_network" "vnet" {
  name                = "vnet-orcaopta"
  address_space       = ["10.1.0.0/16"]
  location            = var.location
  resource_group_name = azurerm_resource_group.rg.name
}

resource "azurerm_subnet" "subnet" {
  name                 = "subnet-orcaopta"
  resource_group_name  = azurerm_resource_group.rg.name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = ["10.1.1.0/24"]
}

# VM
resource "azurerm_linux_virtual_machine" "vm" {
  name                = "vm-orcaopta-api"
  resource_group_name = azurerm_resource_group.rg.name
  location            = var.location
  size                = "Standard_B1s"
  admin_username      = "orcaopta"
  network_interface_ids = [
    azurerm_network_interface.nic.id
  ]
  admin_password = var.admin_password
}

resource "azurerm_network_interface" "nic" {
  name                = "nic-orcaopta"
  location            = var.location
  resource_group_name = azurerm_resource_group.rg.name

  ip_configuration {
    name                          = "internal"
    subnet_id                      = azurerm_subnet.subnet.id
    private_ip_address_allocation = "Dynamic"
  }
}

# Blob Storage
resource "azurerm_storage_account" "sa" {
  name                     = var.storage_account_name
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = var.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

# AKS (Kubernetes)
resource "azurerm_kubernetes_cluster" "aks" {
  name                = "aks-orcaopta"
  location            = var.location
  resource_group_name = azurerm_resource_group.rg.name
  dns_prefix          = "orcaopta"

  default_node_pool {
    name       = "default"
    node_count = 1
    vm_size    = "Standard_B2s"
  }

  identity {
    type = "SystemAssigned"
  }
}
