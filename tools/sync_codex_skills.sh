#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Sync skill directories from this repo into the global Codex skill directory.

Usage:
  tools/sync_codex_skills.sh [--dest PATH] [--prune]

Options:
  --dest PATH  Override the destination skills directory.
               Default: ${CODEX_HOME:-$HOME/.codex}/skills
  --prune      Remove stale symlinks in the destination that still point into
               this repo but no longer map to a valid skill directory.
  -h, --help   Show this help.
EOF
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
DEST_ROOT="${CODEX_HOME:-$HOME/.codex}/skills"
PRUNE=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dest)
      DEST_ROOT="$2"
      shift 2
      ;;
    --prune)
      PRUNE=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

mkdir -p "$DEST_ROOT"

declare -a SKILL_NAMES=()
linked_count=0
skipped_count=0
error_count=0

while IFS= read -r skill_dir; do
  skill_name="$(basename "$skill_dir")"
  skill_file="${skill_dir}/SKILL.md"
  [[ -f "$skill_file" ]] || continue

  SKILL_NAMES+=("$skill_name")
  dest_path="${DEST_ROOT}/${skill_name}"

  if [[ -L "$dest_path" ]]; then
    current_target="$(readlink "$dest_path")"
    if [[ "$current_target" == "$skill_dir" ]]; then
      echo "ok   ${skill_name} -> ${skill_dir}"
      skipped_count=$((skipped_count + 1))
      continue
    fi
    rm "$dest_path"
  elif [[ -e "$dest_path" ]]; then
    echo "skip ${skill_name}: ${dest_path} exists and is not a symlink" >&2
    error_count=$((error_count + 1))
    continue
  fi

  ln -s "$skill_dir" "$dest_path"
  echo "link ${skill_name} -> ${skill_dir}"
  linked_count=$((linked_count + 1))
done < <(find "$REPO_ROOT" -mindepth 1 -maxdepth 1 -type d | sort)

if [[ "$PRUNE" -eq 1 ]]; then
  while IFS= read -r existing; do
    [[ -L "$existing" ]] || continue
    target="$(readlink "$existing")"
    [[ "$target" == "$REPO_ROOT/"* ]] || continue

    skill_name="$(basename "$existing")"
    keep=0
    for current in "${SKILL_NAMES[@]}"; do
      if [[ "$current" == "$skill_name" ]]; then
        keep=1
        break
      fi
    done

    if [[ "$keep" -eq 0 ]]; then
      rm "$existing"
      echo "prune ${skill_name}"
    fi
  done < <(find "$DEST_ROOT" -mindepth 1 -maxdepth 1 -type l | sort)
fi

echo
echo "Repo root:    $REPO_ROOT"
echo "Codex skills: $DEST_ROOT"
echo "Linked:       $linked_count"
echo "Unchanged:    $skipped_count"

if [[ "$error_count" -gt 0 ]]; then
  echo "Conflicts:    $error_count" >&2
  exit 1
fi

echo "Restart Codex to pick up newly added skills."
