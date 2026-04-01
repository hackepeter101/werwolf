#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   ./install.sh [target_directory]
# Example:
#   ./install.sh werwolf

REPO_URL="https://github.com/hackepeter101/werwolf.git"

TARGET_DIR="${1:-$(basename -s .git "$REPO_URL")}"
VENV_DIR=".venv"

log() {
  echo "[install] $*"
}

need_cmd() {
  command -v "$1" >/dev/null 2>&1
}

run_with_sudo() {
  if need_cmd sudo; then
    sudo "$@"
  else
    "$@"
  fi
}

install_python_and_git() {
  log "Python 3 not found. Attempting installation..."

  if need_cmd apt-get; then
    run_with_sudo apt-get update
    run_with_sudo apt-get install -y python3 python3-venv git
  elif need_cmd dnf; then
    run_with_sudo dnf install -y python3 python3-pip python3-virtualenv git
  elif need_cmd yum; then
    run_with_sudo yum install -y python3 python3-pip git
  elif need_cmd pacman; then
    run_with_sudo pacman -Sy --noconfirm python python-virtualenv git
  elif need_cmd zypper; then
    run_with_sudo zypper --non-interactive install python3 python3-pip python3-virtualenv git
  elif need_cmd apk; then
    run_with_sudo apk add --no-cache python3 py3-pip py3-virtualenv git
  else
    echo "Could not detect a supported package manager."
    echo "Please install Python 3, python3-venv (or virtualenv), and git manually."
    exit 1
  fi
}

ensure_python() {
  if ! need_cmd git; then
    log "git not found. Attempting installation..."
    install_python_and_git
  fi

  if ! need_cmd python3; then
    install_python_and_git
  fi

  if ! python3 -m venv --help >/dev/null 2>&1; then
    log "Python venv module not available. Attempting to install..."

    if need_cmd apt-get; then
      run_with_sudo apt-get update
      run_with_sudo apt-get install -y python3-venv
    elif need_cmd dnf; then
      run_with_sudo dnf install -y python3-virtualenv
    elif need_cmd yum; then
      run_with_sudo yum install -y python3-virtualenv
    elif need_cmd pacman; then
      run_with_sudo pacman -Sy --noconfirm python-virtualenv
    elif need_cmd zypper; then
      run_with_sudo zypper --non-interactive install python3-virtualenv
    elif need_cmd apk; then
      run_with_sudo apk add --no-cache py3-virtualenv
    else
      echo "Could not install venv module automatically."
      echo "Please install Python venv support manually."
      exit 1
    fi
  fi
}

clone_repo() {
  if [[ -d "$TARGET_DIR/.git" ]]; then
    log "Repository already exists in '$TARGET_DIR'. Pulling latest changes..."
    git -C "$TARGET_DIR" pull --ff-only
  elif [[ -e "$TARGET_DIR" ]]; then
    echo "Target path '$TARGET_DIR' exists but is not a git repository."
    echo "Choose a different target directory."
    exit 1
  else
    log "Cloning repository from $REPO_URL into '$TARGET_DIR'..."
    git clone "$REPO_URL" "$TARGET_DIR"
  fi
}

create_venv() {
  log "Creating virtual environment in '$TARGET_DIR/$VENV_DIR'..."
  python3 -m venv "$TARGET_DIR/$VENV_DIR"

  log "Upgrading pip in virtual environment..."
  "$TARGET_DIR/$VENV_DIR/bin/pip" install --upgrade pip

  log "Installing art package for ASCII role cards..."
  "$TARGET_DIR/$VENV_DIR/bin/pip" install art

  if [[ -f "$TARGET_DIR/requirements.txt" ]]; then
    log "Installing dependencies from requirements.txt..."
    "$TARGET_DIR/$VENV_DIR/bin/pip" install -r "$TARGET_DIR/requirements.txt"
  fi
}

main() {
  ensure_python
  clone_repo
  create_venv

  log "Done."
  echo "Activate with: source $TARGET_DIR/$VENV_DIR/bin/activate"
}

main
