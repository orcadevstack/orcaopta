terraform {
  backend "s3" {
    bucket         = "orcaopta-terraform-state"
    key            = "global/terraform.tfstate"
    region         = "eu-west-1"
    dynamodb_table = "orcaopta-terraform-lock"
    encrypt        = true
  }
}
