#!make
# ---------------------------------------------------------------------------------------------------------------------
# MAKEFILE for handling DOCKER Image build-x Processes
# ---------------------------------------------------------------------------------------------------------------------
# @purpose: base commands for handling docker image provisioning process using makefile-based targets action calls
# ---------------------------------------------------------------------------------------------------------------------
# @author: Patrick Paechnatz <patrick.paechnatz@gmail.com>
# @version: 1.0.1
# @createdAt: 2024-09-11
# @updatedAt: 2024-11-07
# ---------------------------------------------------------------------------------------------------------------------

# Include functional extensions
-include scripts/make/ops_ext_terminal.mk
-include scripts/make/ops_ext_internal.mk

# Setup makefile init scope
SHELL := /bin/bash
.PHONY: build check push clean help
.DEFAULT_GOAL := help
.SILENT: logout-google login-google login-hub do-prep-gitleaks build push clean check

# Detect current host CPU architecture
UNAME_M := $(shell uname -m | tr '[:upper:]' '[:lower:]')
ifeq ($(UNAME_M),x86_64)
  ARCH = amd64
else ifeq ($(UNAME_M),x64)
  ARCH = x64
else ifeq ($(UNAME_M),arm64)
  ARCH = arm64
else
  $(error unsupported architecture: $(UNAME_M))
endif

# Detect current host operating system
UNAME_S := $(shell uname -s | tr '[:upper:]' '[:lower:]')
ifeq ($(UNAME_S),linux)
	OS = linux
else ifeq ($(UNAME_S),darwin)
	OS = darwin
else
  $(error unsupported operating-system: $(UNAME_S))
endif

# Define local makefile variables
GITLEAKS_VERSION = 8.18.4
GITLEAKS_BINARY = gitleaks
REPORT_PREFIX = local
GITLEAKS_REPORT = $(REPORT_PREFIX)-gitleaks.sarif
TRIVY_REPORT = $(REPORT_PREFIX)-trivy.sarif
CURL_RETRY = 3
CURL_RETRY_DELAY = 3

# Define docker image build meta-data (available img-scanner: 'scout' or 'trivy')
IMAGE_NAME=terrareg
IMAGE_TAG=3.12.2-edp-1
IMAGE_PLATFORMS=linux/amd64,linux/arm64
IMAGE_ARTIFACT_FOLDER=public-cloud
IMAGE_ARTIFACT_URL=europe-west3-docker.pkg.dev
IMAGE_ARTIFACT_PROJECT=nz-mgmt-shared-artifacts-8c85/$(IMAGE_ARTIFACT_FOLDER)
IMAGE_BUILD_TAG_LOCAL=t42-local/$(IMAGE_NAME)
IMAGE_BUILD_TAG=$(IMAGE_ARTIFACT_URL)/$(IMAGE_ARTIFACT_PROJECT)/$(IMAGE_NAME)
IMAGE_BUILDER_NAME=t42_local_bob_v1
IMAGE_PLATFORM_LOCAL=linux/$(ARCH)
# If you're using trivy instead of scout a complete SARIF-Report will be provided as well
IMAGE_SCANNER ?= trivy

# Terminal color encodings
T_FX_INFO = \033[33m
T_FX_WARNING = \033[33m
T_FX_ERROR = \033[31m
T_FX_HIGHLIGHT = \033[34m
T_FX_COMMAND = \033[37m
T_FX_RESET = \033[0m

##-- [ Docker Image Commands ] --

## Clean local project related docker images
clean:
	echo -e "\n$(T_FX_INFO)@INFO$(T_FX_RESET): GROOMING '$(IMAGE_BUILD_TAG):latest', $(IMAGE_BUILD_TAG):$(IMAGE_TAG)\n"

## Prepare and build 'local' docker image version for netbox
build: prepare
	echo -e "\n$(T_FX_INFO)@INFO$(T_FX_RESET): BUILD '$(IMAGE_BUILD_TAG_LOCAL):latest', $(IMAGE_BUILD_TAG_LOCAL):$(IMAGE_TAG) [local-target=$(IMAGE_PLATFORM_LOCAL), builder=$(IMAGE_BUILDER_NAME)]\n"
	docker buildx build --platform $(IMAGE_PLATFORM_LOCAL) \
			-t $(IMAGE_BUILD_TAG_LOCAL):latest \
			-t $(IMAGE_BUILD_TAG_LOCAL):$(IMAGE_TAG) --load . && \
	$(MAKE) check ;

## Prepare and push local build docker image to internal artifactory (check for security issue(s) first)
push: prepare
	echo -e "\n$(T_FX_INFO)@INFO$(T_FX_RESET): BUILD+PUSH '$(IMAGE_BUILD_TAG):latest', $(IMAGE_BUILD_TAG):$(IMAGE_TAG) [target=$(IMAGE_PLATFORMS), builder=$(IMAGE_BUILDER_NAME)]\n"
	docker buildx build --platform $(IMAGE_PLATFORMS) --push \
			-t $(IMAGE_BUILD_TAG):latest \
			-t $(IMAGE_BUILD_TAG):$(IMAGE_TAG) . && \
	$(MAKE) check ;

## Check for possible leaks (using local build image)
check: $(do-prep-gitleaks)
	$(GITLEAKS_BINARY) detect --verbose --no-git --config .gitleaks.toml --no-banner --report-format sarif --report-path $(GITLEAKS_REPORT)
	@if [ "$(IMAGE_SCANNER)" = "trivy" ]; then \
		echo -e "\n$(T_FX_INFO)@INFO$(T_FX_RESET): TRIVY-SCAN '$(IMAGE_BUILD_TAG_LOCAL):latest', $(IMAGE_BUILD_TAG_LOCAL):$(IMAGE_TAG) [scanner=trivy, img=local]\n"; \
		trivy image $(IMAGE_BUILD_TAG_LOCAL):latest --scanners vuln --format sarif --output $(TRIVY_REPORT); \
	elif [ "$(IMAGE_SCANNER)" = "scout" ]; then \
		echo -e "\n$(T_FX_INFO)@INFO$(T_FX_RESET): SCOUT-SCAN '$(IMAGE_BUILD_TAG_LOCAL):latest', $(IMAGE_BUILD_TAG_LOCAL):$(IMAGE_TAG) [scanner=docker/scout, img=local]\n"; \
		docker scout cves $(IMAGE_BUILD_TAG_LOCAL):latest; \
	else \
		echo "$(T_FX_ERROR)@ERROR$(T_FX_RESET): Unknown IMAGE_SCANNER value '$(IMAGE_SCANNER)'."; \
		exit 1; \
	fi

prepare:
	@docker buildx inspect $(IMAGE_BUILDER_NAME) >/dev/null 2>&1 || docker buildx create --use --name $(IMAGE_BUILDER_NAME) --driver docker-container

##-- [ Basic Commands ] --

## Login shortcut to gcp oci/artifactory
login-hub:
	echo -e "\n$(T_FX_INFO)@INFO$(T_FX_RESET): As an alternative to this make declaration, you can also use our $(T_FX_HIGHLIGHT)$$ devbox shell$(T_FX_RESET) approach."
	echo -e "For more information, please refer to the primary documentation (README.md) of this repository."
	echo -e "The corresponding call therefore would be: $(T_FX_COMMAND)$$ devbox login-hub$(T_FX_RESET)"
	echo -e "$(T_FX_RESET)--"
	@if [ -z "$$(gcloud auth print-access-token)" ]; then \
		echo "$(T_FX_WARNING)@WARNING$(T_FX_RESET): No access token found, re-authenticate now ..."; \
		$(MAKE) login-google; \
	else \
		gcloud auth configure-docker $$IMAGE_ARTIFACT_URL; \
		helm registry login -u oauth2accesstoken -p "$$(gcloud auth print-access-token)" $$IMAGE_ARTIFACT_URL; \
	fi

## Login shortcut to gcloud auth
login-google:
	echo -e "\n$(T_FX_INFO)@INFO$(T_FX_RESET): As an alternative to this make declaration, you can also use our $(T_FX_HIGHLIGHT)$$ devbox shell$(T_FX_RESET) approach."
	echo -e "For more information, please refer to the primary documentation (README.md) of this repository."
	echo -e "The corresponding call therefore would be: $(T_FX_COMMAND)$$ devbox login$(T_FX_RESET)"
	echo -e "$(T_FX_RESET)--"
	gcloud auth login
	gcloud auth application-default login

## Logout shortcut to gcloud auth
logout-google:
	echo -e "\n$(T_FX_INFO)@INFO$(T_FX_RESET): As an alternative to this make declaration, you can also use our $(T_FX_HIGHLIGHT)$$ devbox shell$(T_FX_RESET) approach."
	echo -e "For more information, please refer to the primary documentation (README.md) of this repository."
	echo -e "The corresponding call therefore would be: $(T_FX_COMMAND)$$ devbox logout$(T_FX_RESET)"
	echo -e "$(T_FX_RESET)--"
	gcloud auth application-default revoke --quiet
	gcloud auth revoke --all
