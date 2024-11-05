# TerraReg Local DevBox

_This shell contains all tools and scripts for the planned production use of the DEVBOX as an integral part of our project repository structure. Extensions and customisations are not only desired but also allowed at any time - we therefore ask for corresponding merge requests for the package and script section of the `devbox.json` file as well as this documentation._

## Available Scripts

```bash
# call devbox-linked script|action
$ devbox run <script>
# e.g. devbox run help
```

| Script            | Description                                                                                       |
|-------------------|:--------------------------------------------------------------------------------------------------|
| `login`           | authenticate yourself via the gcp api (for terraform and gcloud cli commands)                     |
| `login-hub`       | authenticate yourself via the gcp api at the gcp-artifactory hub (docker images, helm charts etc) |
| `logout`          | log out from the gcp-hub and the gcp-api, delete the local authentication cache                   |
| `update`          | update all gcloud components (should be done once a week)                                         |
| `whoami`          | check current login state for default api access and terraform application auth                   |
| `help`            | print-out this markdown file using glow + bat to show available scripts and alias-sets            |

## Terminal Usage

During your active DevBox-Terminal session, your previous alias commands and shell settings are fully preserved, which means that you should still have access to your terminal-relevant configurations and application facilitation's.

## Links

[![WIKI](https://img.shields.io/badge/Confluence%20DOC-Daily%2FmOPS-black)](https://confluence.bare.pandrosion.org/x/fIK2C)
[![REPO](https://img.shields.io/badge/GitLab%20Branch-release%2F0.1.0-black)](https://gitlab.bare.pandrosion.org/edp/infrastructure/cloud/managed-gcp/cloud-mgmt/ops-devbox-shell)
[![ISSUES](https://img.shields.io/badge/Issues%20for%20Version-0.1.0%20RC%202-blue.svg)](https://gitlab.bare.pandrosion.org/edp/infrastructure/cloud/managed-gcp/cloud-mgmt/ops-devbox-shell/-/boards)
