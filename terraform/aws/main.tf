terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.region
}

# VPC
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
  tags = { Name = "orcaopta-vpc" }
}

resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  map_public_ip_on_launch = true
  tags = { Name = "orcaopta-public-subnet" }
}

# EC2
resource "aws_instance" "api" {
  ami           = var.ami_id
  instance_type = "t3.micro"
  subnet_id     = aws_subnet.public.id

  tags = { Name = "orcaopta-api" }
}

# S3
resource "aws_s3_bucket" "models" {
  bucket = var.s3_bucket_name
}

# EKS (Kubernetes cluster skeleton)
module "eks" {
  source          = "terraform-aws-modules/eks/aws"
  cluster_name    = "orcaopta-eks"
  cluster_version = "1.29"
  subnets         = [aws_subnet.public.id]
  vpc_id          = aws_vpc.main.id
}
