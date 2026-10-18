class EasydpScan < Formula
  desc "Enterprise-grade, offline-first local PII scanner for Indian DPDP Act compliance"
  homepage "https://easydp.in"
  url "https://github.com/easydp-in/pii-scanner/archive/refs/tags/v0.1.0.tar.gz"
  sha256 "REPLACE_WITH_SHA256"
  license "Apache-2.0"

  depends_on "python@3.12"

  def install
    virtualenv_install_with_resources
  end

  test do
    system "#{bin}/easydp-scan", "--version"
  end
end
