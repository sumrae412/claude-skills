#!/bin/bash
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

if [ -z "${GH_TOKEN:-}" ]; then
  echo "GH_TOKEN not set — skipping git auth and repo sync" >&2
  exit 0
fi

git config --global credential.helper '!f() { echo "username=x-access-token"; echo "password=${GH_TOKEN}"; }; f'

REPOS=(
  "toneguard"
  "courierflow"
  "claude-skills"
  "claude-courierflow-memory"
  "claude-config"
)
GITHUB_USER="sumrae412"
TARGET_DIR="/home/user"

for repo in "${REPOS[@]}"; do
  repo_dir="${TARGET_DIR}/${repo}"
  if [ -d "${repo_dir}/.git" ]; then
    git -C "${repo_dir}" pull --ff-only origin HEAD 2>&1 || echo "Warning: failed to pull ${repo}" >&2
  else
    git clone "https://github.com/${GITHUB_USER}/${repo}.git" "${repo_dir}" 2>&1 || echo "Warning: failed to clone ${repo}" >&2
  fi
done
