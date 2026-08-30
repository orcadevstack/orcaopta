class Orcaopta < Formula
  desc "Orcaopta Control Plane CLI"
  homepage "https://github.com/orcadevstack/orcaopta"
  version "0.1.0"

  on_macos do
    if Hardware::CPU.arm?
      url "https://github.com/orcadevstack/orcaopta/releases/download/v0.1.0/orcaopta-macos-arm64.pkg"
      sha256 "<ARM64_SHA256>"
    else
      url "https://github.com/orcadevstack/orcaopta/releases/download/v0.1.0/orcaopta-macos-amd64.pkg"
      sha256 "<AMD64_SHA256>"
    end
  end

  def install
    bin.install "orcaopta"
  end
end
