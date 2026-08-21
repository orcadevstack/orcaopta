terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

# VPC
resource "google_compute_network" "vpc" {
  name                    = "orcaopta-vpc"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "subnet" {
  name          = "orcaopta-subnet"
  ip_cidr_range = "10.2.0.0/24"
  region        = var.region
  network       = google_compute_network.vpc.id
}

# VM
resource "google_compute_instance" "vm" {
  name         = "orcaopta-api-vm"
  machine_type = "e2-micro"
  zone         = var.zone

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-12"
    }
  }

  network_interface {
    subnetwork = google_compute_subnetwork.subnet.id
    access_config {}
  }
}

# GCS bucket
resource "google_storage_bucket" "models" {
  name     = var.bucket_name
  location = var.region
}

# GKE (Kubernetes)
resource "google_container_cluster" "gke" {
  name     = "orcaopta-gke"
  location = var.region
  network  = google_compute_network.vpc.id
  subnetwork = google_compute_subnetwork.subnet.name

  remove_default_node_pool = true
  initial_node_count       = 1

  node_pool {
    name       = "default-pool"
    node_count = 1

    node_config {
      machine_type = "e2-medium"
    }
  }
}
