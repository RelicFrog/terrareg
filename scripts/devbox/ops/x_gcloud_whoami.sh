#!/usr/bin/env bash
# --
# @version: 0.1.1
# @purpose: Shell script to identify yourself within gcloud api authentication scope
# --

if echo "" | gcloud projects list &> /dev/null
then
  C_DBX_INIT_GCP_ACCOUNT_CURRENT=$(gcloud config list account --format "value(core.account)")
  echo "Great! You are still logged in as $C_DBX_INIT_GCP_ACCOUNT_CURRENT"
else
  echo "Sorry, you're logged-out, please re-authenticate using 'devbox run login'"
fi
