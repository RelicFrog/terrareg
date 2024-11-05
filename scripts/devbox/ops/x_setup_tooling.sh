#!/usr/bin/env bash
# --
# @version: 0.1.1
# @purpose: Shell script to setup local tooling
# --

if [ "$(uname -m)" == "aarch64" ]; then arch=arm64; else arch=amd64; fi
wget https://github.com/terraform-docs/terraform-docs/releases/download/v0.16.0/d-v0.16.0-linux-${arch}.tar.gz && tar -zxvf terraform-docs-v0.16.0-linux-${arch}.tar.gz terraform-docs && chmod +x terraform-docs && mv terraform-docs ./bin/ && rm terraform-docs-v0.16.0-linux-${arch}.tar.gz
wget https://github.com/aquasecurity/tfsec/releases/download/v1.26.0/tfsec-linux-${arch} -O ./bin/tfsec && chmod +x ./bin/tfsec
wget https://github.com/infracost/infracost/releases/download/v0.10.10/infracost-linux-${arch}.tar.gz && tar -zxvf infracost-linux-${arch}.tar.gz infracost-linux-${arch} && mv infracost-linux-${arch} ./bin/infracost && chmod +x ./bin/infracost && rm infracost-linux-${arch}.tar.gz
