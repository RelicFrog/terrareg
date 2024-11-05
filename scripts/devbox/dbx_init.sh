#!/usr/bin/env bash
# --
# @version: 1.0.0
# @purpose: Shell script to run when an interactive devbox shell is started.
# --

#
# constants and variable scope
# --
C_DBX_INIT_PATH_ROOT="scripts/devbox/init"
C_DBX_INIT_ENTRYPOINT="dbx_init.sh"

#
# function: check baseline configuration and tool/package availability
# --
init_check() {

  # @info: this os identification process will be used later to provide additional init-scripts based on your os
  unameOut=$(uname -a)
  case "${unameOut}" in
    *Microsoft*)  C_DBX_OS="WSL"     ; C_DBX_INIT_PATH="${C_DBX_INIT_PATH_ROOT}/os_win64wsl" ;;
    *microsoft*)  C_DBX_OS="WSL2"    ; C_DBX_INIT_PATH="${C_DBX_INIT_PATH_ROOT}/os_win64wsl" ;;
    Linux*)       C_DBX_OS="Linux"   ; C_DBX_INIT_PATH="${C_DBX_INIT_PATH_ROOT}/os_linux"    ;;
    Darwin*)      C_DBX_OS="Mac"     ; C_DBX_INIT_PATH="${C_DBX_INIT_PATH_ROOT}/os_darwin"   ;;
    CYGWIN*)      C_DBX_OS="Cygwin"  ; C_DBX_INIT_PATH="${C_DBX_INIT_PATH_ROOT}/os_win64"    ;;
    MINGW*)       C_DBX_OS="Windows" ; C_DBX_INIT_PATH="${C_DBX_INIT_PATH_ROOT}/os_win64"    ;;
    *Msys)        C_DBX_OS="Windows" ; C_DBX_INIT_PATH="${C_DBX_INIT_PATH_ROOT}/os_win64"    ;;
    *)            C_DBX_OS="???:${unameOut}"
  esac

  echo "------------------------------------------------------------------------------------------------------------------";
  echo "Welcome to ${C_DBX_META_TEAM}/${C_DBX_META_TEAM_ID} DevBox-Shell v${C_DBX_META_VERSION} | See DEVBOX.md for tips and tasks on using this terminal ...";
  echo "------------------------------------------------------------------------------------------------------------------";
  #
  # check devbox core requirements and differ between project and standalone mode
  # --
  if [ ! -f "$C_DBX_INIT_PATH_ROOT/../$C_DBX_INIT_ENTRYPOINT" ]
  then
    echo "ERROR : devbox init-path not found, therefore devbox couldn't bootstrap baseline config. Check devbox integration first!"
    echo "LINK  : https://gitlab.bare.pandrosion.org/edp/infrastructure/cloud/managed-gcp/cloud-mgmt/ops-devbox-shell"
    exit 1
  else
    echo "◼︎ check : devbox init script available ✔︎"
  fi

  # ***
  # *** @TBD: add os specific init scripts (currently not implemented yet)
  # ***
  # --
  # echo "◼︎ check : init os-related bootstrap scripts at [./${C_DBX_INIT_PATH}] for [${C_DBX_OS}] ✔"

  #
  # check gcloud-sdk installation/availability
  # --
  if ! command -v gcloud &> /dev/null
  then
    echo "ERROR : local gcloud binary not available, check required packages/setup first!"
    echo "LINK  : https://cloud.google.com/sdk/docs/install-sdk"
    exit 1
  else
    echo "◼︎ check : gcloud sdk is available ✔︎"
  fi

  #
  # check terraform installation/availability
  # --
  if ! command -v terraform &> /dev/null
  then
    echo "ERROR : local terraform binary not available, check required packages/setup first!"
    echo "LINK  : https://developer.hashicorp.com/terraform/install"
    exit 1
  else
    echo "◼︎ check : terraform is available ✔︎"
  fi

  #
  # check terragrunt installation/availability
  # --
  if ! command -v terragrunt &> /dev/null
  then
    echo "ERROR : local terragrunt binary not available, check required packages/setup first!"
    echo "LINK  : https://terragrunt.gruntwork.io/docs/getting-started/install/"
    exit 1
  else
    echo "◼︎ check : terragrunt is available ✔︎"
  fi

  #
  # check terraform-docs installation/availability
  # --
  if ! command -v terraform-docs &> /dev/null
  then
    echo "ERROR : local terraform-docs binary not available, check required packages/setup first!"
    echo "LINK  : https://github.com/terraform-docs/terraform-docs"
    exit 1
  else
    echo "◼︎ check : terraform-docs is available ✔︎"
  fi

  #
  # check tfsec installation/availability
  # --
  if ! command -v tfsec &> /dev/null
  then
    echo "ERROR : local tfsec binary not available, check required packages/setup first!"
    echo "LINK  : https://github.com/aquasecurity/tfsec"
    exit 1
  else
    echo "◼︎ check : tfsec is available ✔︎"
  fi

  #
  # check infracost installation/availability
  # --
  if ! command -v infracost &> /dev/null
  then
    echo "ERROR : local infracost binary not available, check required packages/setup first!"
    echo "LINK  : https://github.com/infracost/infracost"
    exit 1
  else
    echo "◼︎ check : infracost is available ✔︎"
  fi
}

#
# function: print out some useful information after devbox init-phase
# --
init_print_help () {
  echo "------------------------------------------------------------------------------------------------------------------";
  echo "Available project scripts (excerpt)"
  echo "------------------------------------------------------------------------------------------------------------------";
  echo "$ none"
  echo "------------------------------------------------------------------------------------------------------------------";
  echo "Available core/system scripts (excerpt)"
  echo "------------------------------------------------------------------------------------------------------------------";
  echo "$ devbox run login           | login into gcp api (sdk/tf-provider) related project resources"
  echo "$ devbox run login-hub       | login into gcp artifactory resources (docker image repo and helm repo)"
  echo "$ devbox run logout          | logout from all gcp resources, based on your current terminal session"
  echo "$ devbox run api-update      | run gcloud component update process"
  echo "$ devbox run api-prep        | prepare api related gcp endpoint activation"
  echo "$ devbox run whoami          | check your current authentication state for all gcp related api resources"
  echo "$ devbox run help            | print out devbox project documentation, show/describe all scripts available"
  echo "------------------------------------------------------------------------------------------------------------------";
  echo "type 'devbox run help' (or <your-dbx-run-alias> help) to show scripts/doc/dbx_main.md devbox-shell documentation"
  echo "type 'exit' to close this shell and return to your os-source terminal | os-shell"
  if [ -f "$C_DBX_INIT_SESSION_FILE_MARKER" ]; then
    echo "------------------------------------------------------------------------------------------------------------------";
    echo "You are in an active tmux session; use tmux-command (control+b) <arrow-up>|<arrow-down> to switch between your"
    echo "active panes. The first pane will be on the top of your screen and handle all devbox shell commands. The second"
    echo -e "pane will be on the bottom you your screen and handle tunnel-connection to ice-api etc.\n"
  fi
  if  cmp --silent -- devbox.json devbox.json.default ; then
      echo -e "\033[0m------------------------------------------------------------------------------------------------------------------"
      echo -e "\033[33m@INFO\033[0m: Currently you are using a simple copy of the default configuration for this devbox shell."
      echo -e "You can make your own adjustments to the resulting\033[34m$$ devbox.json\033[0m file at any time to customise"
      echo -e "the shell according to your needs. Check official reference information at:"
      echo -e "\033[37mhttps://www.jetify.com/devbox/docs/configuration/\033[0m"
      echo -e "\033[0m------------------------------------------------------------------------------------------------------------------"
  fi
}

#
# shell entrypoint(s)
# --

init_check
init_print_help
