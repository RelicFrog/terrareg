#!make
# ---------------------------------------------------------------------------------------------------------------------
# MAKEFILE for handling GKE-Cluster, GCP-Auth and DOCKER Image build-x Processes
# ---------------------------------------------------------------------------------------------------------------------
# @purpose: base commands for handling GCP related provisioning process using makefile-based targets action calls
# ---------------------------------------------------------------------------------------------------------------------
# @author: Patrick Paechnatz <patrick.paechnatz@gmail.com>
# @version: 1.0.2
# @createdAt: 2024-09-11
# @updatedAt: 2024-11-08
# ---------------------------------------------------------------------------------------------------------------------

# Include functional extensions
-include scripts/make/ops_ext_terminal.mk
-include scripts/make/ops_ext_internal.mk

# Setup makefile init scope
SHELL := /bin/bash
.PHONY: gcp-cloudsql-create gcp-cloudsql-destroy gke-cluster-preflight gke-cluster-create gke-cluster-destroy gke-cluster-auth gke-cluster-sa-reset gke-extend-iam api-prep api-update logout-google login-google login-hub do-prep-gitleaks build push clean check
.SILENT: gcp-cloudsql-create gcp-cloudsql-destroy gke-cluster-preflight gke-cluster-create gke-cluster-destroy gke-cluster-auth gke-cluster-sa-reset gke-extend-iam api-prep api-update logout-google login-google login-hub do-prep-gitleaks build push clean check
.DEFAULT_GOAL := help

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

# Define export vars
export GCP_PROJECT_ID=ordinal-idea-428811-f9
export GCP_PROJECT_NUM=734428111519
export GCP_TENANT=terrareg
export GCS_BUCKET=$(GCP_TENANT)-exhy4dxkx2bkupze
export GCP_SA_ID=$(GCP_TENANT)-ops
export GKE_CLUSTER_NAME=$(GCP_TENANT)-green
export GKE_CLUSTER_REGION=europe-west3
export GKE_CLUSTER_CHANNEL=stable
export GCP_CLOUD_SQL_VERSION=MYSQL_8_0
export GCP_CLOUD_SQL_TIER=db-f1-micro
export GCP_CLOUD_SQL_STORAGE_SIZE=10GB

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
	        --build-arg VERSION=v$(IMAGE_TAG) \
			-t $(IMAGE_BUILD_TAG_LOCAL):latest \
			-t $(IMAGE_BUILD_TAG_LOCAL):$(IMAGE_TAG) --load . && \
	$(MAKE) check ;

## Prepare and push local build docker image to internal artifactory (todo: check for security issue(s) first)
push: prepare
	echo -e "\n$(T_FX_INFO)@INFO$(T_FX_RESET): BUILD+PUSH '$(IMAGE_BUILD_TAG):latest', $(IMAGE_BUILD_TAG):$(IMAGE_TAG) [target=$(IMAGE_PLATFORMS), builder=$(IMAGE_BUILDER_NAME)]\n"
	docker buildx build --platform $(IMAGE_PLATFORMS) --push \
	        --build-arg VERSION=v$(IMAGE_TAG) \
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

## GCP API Updates
api-update:
	echo -e "\033[33m@INFO\033[0m: As an alternative to this make declaration, you can also use our \033[34m$$ devbox shell\033[0m approach."
	echo -e "For more information, please refer to the primary documentation (README.md) of this repository."
	echo -e "The corresponding call therefore would be: \033[37m$$ devbox run api-update\033[0m"
	echo -e "\033[0m"
	echo "[make/cmd] disable Usage Reporting ..."
	gcloud config set disable_usage_reporting true &> /dev/null
	echo "[make/cmd] update GCloud Components now ..."
	gcloud components update

## GCP API Preflight Procedures
api-prep:
	echo -e "\033[33m@INFO\033[0m: As an alternative to this make declaration, you can also use our \033[34m$$ devbox shell\033[0m approach."
	echo -e "For more information, please refer to the primary documentation (README.md) of this repository."
	echo -e "The corresponding call therefore would be: \033[37m$$ devbox run api-prep\033[0m"
	echo -e "\033[0m"
	echo "[make/cmd] disable usage reporting ..."
	gcloud config set disable_usage_reporting true &> /dev/null
	echo "[make/cmd] update GCloud Components now ..."
	gcloud components update
	echo "[make/cmd] activate api endpoints required for this project ..."
	gcloud services enable container.googleapis.com
	gcloud services enable compute.googleapis.com
	gcloud services enable iam.googleapis.com
	gcloud services enable logging.googleapis.com
	gcloud services enable monitoring.googleapis.com
	gcloud services enable sqladmin.googleapis.com

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

## Login shortcut to docker hub
login-docker:
	echo -e "\n$(T_FX_INFO)@INFO$(T_FX_RESET): As an alternative to this make declaration, you can also use our $(T_FX_HIGHLIGHT)$$ devbox shell$(T_FX_RESET) approach."
	echo -e "For more information, please refer to the primary documentation (README.md) of this repository."
	echo -e "The corresponding call therefore would be: $(T_FX_COMMAND)$$ devbox login-docker$(T_FX_RESET)"
	echo -e "$(T_FX_RESET)--"
	docker login

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

##-- [ Quick Commands for GKE/GCP ] --

## Quick GKE-cluster destroy
gke-cluster-destroy:
	echo -e "$(T_FX_INFO)@INFO$(T_FX_RESET): GCP GKE Cluster is now being destroyed ... This may take a few minutes depending on the cluster size.\n"
	echo "[make/cmd] init | Checking if Cluster exists ..."
	if gcloud container clusters describe $$GKE_CLUSTER_NAME --region=$$GKE_CLUSTER_REGION --project=$$GCP_PROJECT_ID >/dev/null 2>&1; then \
		echo "[make/cmd] GKE-Cluster '$$GKE_CLUSTER_NAME' found, proceeding with deletion ..."; \
		gcloud container clusters delete $$GKE_CLUSTER_NAME \
			--region=$$GKE_CLUSTER_REGION \
			--project=$$GCP_PROJECT_ID \
			--quiet; \
		echo "[make/cmd] GKE-Cluster '$$GKE_CLUSTER_NAME' deletion complete."; \
	else \
		echo "[make/cmd] GKE-Cluster '$$GKE_CLUSTER_NAME' does not exist, skipping deletion ..."; \
	fi
	echo "[make/cmd] gke-cluster-destroy process complete +++"

## Quick GKE-cluster create
gke-cluster-create: gke-cluster-preflight
	echo -e "$(T_FX_INFO)@INFO$(T_FX_RESET): GCP GKE Cluster is now being created ... This can take up to\033[37m 10\033[0m minutes depending on available resources!\n"
	echo "[make/cmd] init | Checking if Cluster exists and all preflight requirements are met ..."
	if ! gcloud iam service-accounts describe $$GCP_SA_ID@$$GCP_PROJECT_ID.iam.gserviceaccount.com >/dev/null 2>&1; then \
		echo "[make/cmd] SA not found, please call 'make gke-create-sa' first!"; \
	elif gcloud container clusters describe $$GKE_CLUSTER_NAME --region=$$GKE_CLUSTER_REGION --project=$$GCP_PROJECT_ID >/dev/null 2>&1; then \
		echo "[make/cmd] GKE-Cluster '$$GKE_CLUSTER_NAME' already exists, skipping creation ..."; \
	else \
		echo "[make/cmd] All requirements met, creating autopilot GKE-Cluster '$$GKE_CLUSTER_NAME' now ..."; \
		gcloud container clusters create-auto $$GKE_CLUSTER_NAME \
			--location=$$GKE_CLUSTER_REGION \
			--release-channel=$$GKE_CLUSTER_CHANNEL \
			--project=$$GCP_PROJECT_ID \
			--service-account=$$GCP_SA_ID@$$GCP_PROJECT_ID.iam.gserviceaccount.com; \
		echo "[make/cmd] GKE-Cluster creation complete."; \
	fi

## Quick GKE-cluster service-account reset
gke-cluster-sa-reset:
	echo -e "$(T_FX_INFO)@INFO$(T_FX_RESET): Service Account and associated IAM policy bindings are being de-provisioned ...\n"
	echo "[make/cmd] init | Checking if Service Account exists ..."
	if gcloud iam service-accounts describe $$GCP_SA_ID@$$GCP_PROJECT_ID.iam.gserviceaccount.com >/dev/null 2>&1; then \
		echo "[make/cmd] Service Account '$$GCP_SA_ID' found, proceeding with deletion ..."; \
		gcloud iam service-accounts delete $$GCP_SA_ID@$$GCP_PROJECT_ID.iam.gserviceaccount.com --quiet; \
		echo "[make/cmd] Service Account '$$GCP_SA_ID' and associated IAM bindings deleted successfully."; \
	else \
		echo "[make/cmd] Service Account '$$GCP_SA_ID' does not exist, skipping deletion ..."; \
	fi
	echo "[make/cmd] sa-cleanup-process complete +++"

## Quick GKE-cluster auth
gke-cluster-auth:
	echo -e "\033[33m@INFO\033[0m: Login to GKE Cluster '$$GKE_CLUSTER_NAME' ...\n"
	echo "[make/cmd] init | Checking if Cluster exists ..."
	if gcloud container clusters describe $$GKE_CLUSTER_NAME --region=$$GKE_CLUSTER_REGION --project=$$GCP_PROJECT_ID >/dev/null 2>&1; then \
		echo "[make/cmd] GKE-Cluster '$$GKE_CLUSTER_NAME' found, proceeding with authentication ..."; \
		gcloud container clusters get-credentials $$GKE_CLUSTER_NAME --region $$GKE_CLUSTER_REGION --project $$GCP_PROJECT_ID; \
	else \
		echo "[make/cmd] GKE-Cluster '$$GKE_CLUSTER_NAME' does not exist, check cluster status first!"; \
	fi; \
	echo "[make/cmd] GKE-auth-process complete +++"

## Quick GKE-cluster iam-extend-task
gke-extend-iam:
	echo "[make/cmd] activate IAM policy bindings for GKE/GCP ..."; \
	for role in "roles/iam.serviceAccountUser" "roles/container.clusterAdmin" "roles/container.admin" "roles/compute.admin" "roles/storage.objectAdmin" "roles/dns.admin" "roles/certificatemanager.editor" "roles/workloadcertificate.admin" "roles/compute.networkAdmin" "roles/cloudsql.client"; do \
		echo "[make/cmd] checking if '$$role' is already bound to service account ..."; \
		if ! gcloud projects get-iam-policy $$GCP_PROJECT_NUM --flatten="bindings[].members" --format="value(bindings.role)" --filter="bindings.members:serviceAccount:$$GCP_SA_ID@$$GCP_PROJECT_ID.iam.gserviceaccount.com AND bindings.role=$$role" | grep -q "$$role"; then \
			echo "[make/cmd] binding '$$role' to new gke-service-account ..."; \
			gcloud projects add-iam-policy-binding $$GCP_PROJECT_NUM --member="serviceAccount:$$GCP_SA_ID@$$GCP_PROJECT_ID.iam.gserviceaccount.com" --role="$$role"; \
		else \
			echo "[make/cmd] '$$role' is already bound, skipping ..."; \
		fi; \
	done; \
	echo "[make/cmd] all roles assigned successfully."; \

## Quick GKE-cluster preflight
gke-cluster-preflight:
	echo -e "$(T_FX_INFO)@INFO$(T_FX_RESET): GCP GKE Cluster will now be prepared ...\n"
	echo "[make/cmd] init | create GCE bucket ..."
	if ! gcloud storage buckets list --project=$$GCP_PROJECT_ID --filter="name:$$GCS_BUCKET" --format="value(name)" | grep -q $$GCS_BUCKET; then \
		gcloud storage buckets create gs://$$GCS_BUCKET --project $$GCP_PROJECT_ID --location $$GKE_CLUSTER_REGION; \
		echo "[make/cmd] init | Bucket $$GCS_BUCKET created."; \
	else \
		echo "[make/cmd] init | Bucket $$GCS_BUCKET already exists."; \
	fi
	echo "[make/cmd] init | Checking if SA exists ..."
	if ! gcloud iam service-accounts describe $$GCP_SA_ID@$$GCP_PROJECT_ID.iam.gserviceaccount.com >/dev/null 2>&1; then \
		echo "[make/cmd] init | SA not found, creating now ..."; \
		gcloud iam service-accounts create $$GCP_SA_ID --description="boring-registry gke+gcs service-account (for all operations)" --display-name="SA for Boring-Registry GKE/GCE (Ops)"; \
		echo "[make/cmd] init | checking and activating GCS access policy ..."; \
		if ! gsutil iam get gs://$$GCS_BUCKET | grep -q "serviceAccount:$$GCP_SA_ID@$$GCP_PROJECT_ID.iam.gserviceaccount.com.*roles/storage.objectAdmin"; then \
			echo "[make/cmd] binding 'storage.objectAdmin' role to service account on bucket ..."; \
			gsutil iam ch serviceAccount:$$GCP_SA_ID@$$GCP_PROJECT_ID.iam.gserviceaccount.com:roles/storage.objectAdmin gs://$$GCS_BUCKET; \
		else \
			echo "[make/cmd] init | 'storage.objectAdmin' role is already bound to service account on bucket, skipping ..."; \
		fi; \
		echo "[make/cmd] init | GCS access policy assignment complete."; \
		echo "[make/cmd] init | activate IAM policy bindings for GKE/BR ..."; \
		for role in "roles/iam.serviceAccountUser" "roles/container.clusterAdmin" "roles/container.admin" "roles/compute.admin" "roles/storage.objectAdmin" "roles/dns.admin" "roles/certificatemanager.editor" "roles/workloadcertificate.admin" "roles/compute.networkAdmin" "roles/cloudsql.client"; do \
			echo "[make/cmd] init | checking if '$$role' is already bound to service account ..."; \
			if ! gcloud projects get-iam-policy $$GCP_PROJECT_NUM --flatten="bindings[].members" --format="value(bindings.role)" --filter="bindings.members:serviceAccount:$$GCP_SA_ID@$$GCP_PROJECT_ID.iam.gserviceaccount.com AND bindings.role=$$role" | grep -q "$$role"; then \
				echo "[make/cmd] init | binding '$$role' to new gke-service-account ..."; \
				gcloud projects add-iam-policy-binding $$GCP_PROJECT_NUM --member="serviceAccount:$$GCP_SA_ID@$$GCP_PROJECT_ID.iam.gserviceaccount.com" --role="$$role"; \
			else \
				echo "[make/cmd] init | '$$role' is already bound, skipping ..."; \
			fi; \
		done; \
		echo "[make/cmd] init | all roles assigned successfully."; \
	else \
		echo "[make/cmd] init | SA already exists, skipping creation/alignment process ..."; \
	fi
	echo "[make/cmd] init | preflight complete +++"; \

##-- [ GCP Cloud SQL Commands ] --

## Install Lightweight MySQL Instance using CloudSQL

gcp-cloudsql-create:
	echo -e "$(T_FX_INFO)@INFO$(T_FX_RESET): GCP CloudSQL instance will now be prepared ... $(T_FX_RESET)";
	@if gcloud sql instances describe $$GCP_TENANT-mysql-instance --format="value(name)" > /dev/null 2>&1; then \
		echo "[make/cmd] cloudSQL instance '$$GCP_TENANT-mysql-instance' already exists. Skipping creation."; \
	else \
		gcloud sql instances create $$GCP_TENANT-mysql-instance \
			--database-version=$$GCP_CLOUD_SQL_VERSION \
			--tier=$$GCP_CLOUD_SQL_TIER \
			--region=$$GKE_CLUSTER_REGION \
			--root-password=$$C_DBX_APP_GCP_CLOUDSQL_PASSWORD \
			--storage-size=$$GCP_CLOUD_SQL_STORAGE_SIZE; \
		echo "[make/cmd] cloud-sql | instance provisioning complete +++"; \
	fi

## Delete MySQL Instance (CloudSQL)

gcp-cloudsql-delete:
	echo -e "$(T_FX_INFO)@INFO$(T_FX_RESET): GCP CloudSQL instance will now be deleted ... $(T_FX_RESET)";
	@if gcloud sql instances describe $$GCP_TENANT-mysql-instance --format="value(name)" > /dev/null 2>&1; then \
		gcloud sql instances delete $$GCP_TENANT-mysql-instance --quiet; \
		echo "[make/cmd] cloud-sql | instance de-provisioning complete +++"; \
	else \
		echo "[make/cmd] cloudSQL instance '$$GCP_TENANT-mysql-instance' does not exists. Skipping deletion."; \
	fi

##-- [ Common GKE Payloads ] --

## Install Lightweight Traefik in Debug-Mode
traefik-update:
	helm upgrade --install traefik traefik/traefik -f manifests/common/traefik/values.yaml --namespace traefik --create-namespace

## Remove Traefik from Cluster
traefik-destroy:
	helm delete traefik --namespace traefik

