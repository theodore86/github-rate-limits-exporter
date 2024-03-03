#!/usr/bin/env bash
set -eo pipefail

OS=$(echo $(uname) | tr '[:upper:]' '[:lower:]')

_arch() {
  local _arch='amd64'
  [[ "$(uname -m)" == 'x86_64' ]] && _arch='amd64'
  [[ "$(uname -m)" == 'aarch64' ]] && _arch='arm64'
  echo "${_arch}"
}


_helmfile() {
  local helmfile_version='v0.162.0'
  local helmfile_location="https://github.com/helmfile/helmfile/releases/download/${helmfile_version}"
  local helmfile_filename="helmfile_${helmfile_version:1}_${OS}_$(_arch).tar.gz"
  local _return=1
  curl --retry 5 --retry-connrefused -LO "${helmfile_location}/${helmfile_filename}" && \
  tar zxf "${helmfile_filename}" && rm -f "${helmfile_filename}" && \
  chmod +x helmfile && \
  mv helmfile /usr/local/bin/helmfile && \
  helmfile -v 2>/dev/null && \
  helmfile init --force 2>/dev/null && \
  _return=0
  return "${_return}"
}


_helm() {
  local helm_version='v3.14.1'
  local helm_location='https://get.helm.sh'
  local helm_filename="helm-${helm_version}-${OS}-$(_arch).tar.gz"
  local _return=1
  curl --retry 5 --retry-connrefused -LO "${helm_location}/${helm_filename}" && \
  tar zxf "${helm_filename}" && \
  mv linux-amd64/helm /usr/local/bin/helm && \
  rm -rf ./linux-amd64 "${helm_filename}" && \
  echo -e "\nhelm version:" && \
  helm version 2>/dev/null && \
  source <(helm completion bash 2>/dev/null) && \
  _return=0
  return "${_return}"
}


_kind() {
  local kind_version='v0.20.0'
  local kind_location="https://github.com/kubernetes-sigs/kind/releases/download/${kind_version}"
  local kind_filename="kind-${OS}-$(_arch)"
  local _return=1
  curl --retry 5 --retry-connrefused -LO "${kind_location}/${kind_filename}" && \
  chmod +x "./${kind_filename}" && \
  mv "./${kind_filename}" /usr/local/bin/kind && \
  echo -e "\nKIND version:" && \
  kind version && \
  source <(kind completion bash 2>/dev/null) && \
  rm -rf "${kind_filename}" && \
  _return=0
  return "${_return}"
}


main() {
  _helm || { echo "Helm install failed" && exit 1; }
  _helmfile || { echo "Helmfile install failed" && exit 1; }
  _kind || { echo "KIND install failed" && exit 1; }
}


main
