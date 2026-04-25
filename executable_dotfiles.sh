#!/bin/sh
# -*-mode:sh-*- vim:ft=shell-script

# ~/dotfiles.sh
# =============================================================================
# Idempotent manual setup script to install or update shell dependencies.

set -e

command_exists() {
    command -v "$@" >/dev/null 2>&1
}

error() {
    printf -- "%sError: $*%s\n" >&2 "$RED" "$RESET"
}

setup_color() {
    # Only use colors if connected to a terminal
    if [ -t 1 ]; then
        RED=$(printf '\033[31m')
        GREEN=$(printf '\033[32m')
        # YELLOW=$(printf '\033[33m')
        BLUE=$(printf '\033[34m')
        BOLD=$(printf '\033[1m')
        RESET=$(printf '\033[m')
    else
        RED=""
        GREEN=""
        # YELLOW=""
        BLUE=""
        BOLD=""
        RESET=""
    fi
}

import_repo() {
    repo=$1
    destination=$2
    if uname | grep -Eq '^(cygwin|mingw|msys)'; then
        uuid=$(powershell -NoProfile -Command "[guid]::NewGuid().ToString()")
    else
        uuid=$(uuidgen)
    fi
    TMPFILE=$(mktemp /tmp/dotfiles."${uuid}".tar.gz) || exit 1
    curl -s -L -o "$TMPFILE" "$repo" || exit 1
    # chezmoi import --strip-components 1 --destination "$destination" "$TMPFILE" || exit 1
    rm -f "$TMPFILE"
}

setup_dependencies() {
    printf -- "\n%sSetting up dependencies:%s\n\n" "$BOLD" "$RESET"

    # Install Homebrew packages
    if command -v brew > /dev/null; then
        printf -- "%sInstalling/updating apps using Homebrew...%s\n" "$BLUE" "$RESET"
        brew bundle --global
    fi

    # Install Rust
    printf -- "%sInstalling/updating Rust...%s\n" "$BLUE" "$RESET"
    if ! command -v rustup > /dev/null; then
      curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
    else 
      rustup update
    fi

    # Install SDKManager
    printf -- "%sInstalling/updating SDKManager...%s\n" "$BLUE" "$RESET"
    if ! command -v sdk > /dev/null; then
      curl -s "https://get.sdkman.io" | bash
    else 
      sdk selfupdate
    fi
}

setup_prompts() {
    printf -- "\n%sSetting up shell frameworks:%s\n\n" "$BOLD" "$RESET"
}

setup_applications() {
    printf -- "\n%sSetting up CLI applications:%s\n\n" "$BOLD" "$RESET"
    printf -- "\n%sInstalling Neovim:%s\n\n" "$BLUE" "$RESET"
    if ! command -v nvim > /dev/null; then
      curl -s https://raw.githubusercontent.com/LunarVim/LunarVim/rolling/utils/installer/install-neovim-from-release | sudo bash /dev/stdin
    fi
}

setup_ai_tools() {
    printf -- "\n%sSetting up AI tools:%s\n\n" "$BOLD" "$RESET"

    if command_exists corepack; then
        corepack enable
    fi

    command_exists pnpm || {
        error "pnpm is not installed"
        exit 1
    }

    printf -- "%sInstalling/updating Pi and Pi Agent Browser...%s\n" "$BLUE" "$RESET"
    pnpm add -g @mariozechner/pi-coding-agent pi-agent-browser-native

    command_exists pi || {
        error "pi is not installed"
        exit 1
    }

    command_exists gh || {
        error "gh is not installed"
        exit 1
    }

    printf -- "%sInstalling/updating Pi packages...%s\n" "$BLUE" "$RESET"
    pi install npm:pi-claude-cli
    pi install npm:pi-worktrunk
    pi install npm:@carter-mcalister/pi-worktrunk
    pi install npm:pi-rewind-hook
    pi install npm:pi-agent-browser-native
    pi install npm:pi-subagents

    printf -- "%sInstalling/updating Claude Code Proxy...%s\n" "$BLUE" "$RESET"
    if [ ! -d "$HOME/claude-code-proxy" ]; then
        gh repo clone KaviiSuri/claude-code-proxy "$HOME/claude-code-proxy"
    fi
    (
        cd "$HOME/claude-code-proxy"
        npm install
        npm run build
        npm link
    )
}

setup_tmux_plugins() {
    printf -- "\n%sSetting up tmux plugins:%s\n\n" "$BOLD" "$RESET"

    command_exists git || {
        error "git is not installed"
        exit 1
    }

    TPM_PARENT="$HOME/.tmux/plugins"
    TPM_REPO="$TPM_PARENT/tpm"

    mkdir -p "$TPM_PARENT"

    if [ ! -d "$TPM_REPO/.git" ]; then
        printf -- "%sCloning TPM...%s\n" "$BLUE" "$RESET"
        git clone https://github.com/tmux-plugins/tpm "$TPM_REPO"
    else
        printf -- "%sUpdating TPM...%s\n" "$BLUE" "$RESET"
        git -C "$TPM_REPO" pull --ff-only
    fi

    if command_exists tmux; then
        printf -- "%sInstalling tmux plugins with TPM...%s\n" "$BLUE" "$RESET"
        if tmux ls >/dev/null 2>&1; then
            tmux source-file "$HOME/.config/tmux/tmux.conf" || true
        fi
        "$TPM_REPO/bin/install_plugins" || true
    fi
}

setup_patched_tools() {
    printf -- "\n%sSetting up patched tools:%s\n\n" "$BOLD" "$RESET"

    command_exists git || {
        error "git is not installed"
        exit 1
    }

    command_exists cargo || {
        error "cargo is not installed"
        exit 1
    }

    ILMARI_PARENT="$HOME/code/KaviiSuri"
    ILMARI_REPO="$ILMARI_PARENT/ilmari"

    printf -- "%sInstalling/updating patched Ilmari...%s\n" "$BLUE" "$RESET"
    mkdir -p "$ILMARI_PARENT"

    if [ ! -d "$ILMARI_REPO/.git" ]; then
        git clone git@github.com:KaviiSuri/ilmari.git "$ILMARI_REPO"
    else
        git -C "$ILMARI_REPO" pull --ff-only
    fi

    cargo install --path "$ILMARI_REPO" --force
}

# shellcheck source=/dev/null
setup_devtools() {
    printf -- "\n%sSetting up development tools:%s\n\n" "$BOLD" "$RESET"

    command_exists git || {
        error "git is not installed"
        exit 1
    }

    # Install ASDF Versionn Manager
    # https://asdf-vm.com/
    if ! command -v brew > /dev/null; then
        printf -- "%sInstalling/updating ASDF Extendable Version Manager...%s\n" "$BLUE" "$RESET"
        export ASDF_DIR="${ASDF_DIR:-$HOME/.asdf}" && (
            ASDF_NEW=false
            if [ ! -d "$ASDF_DIR" ]; then
                git clone https://github.com/asdf-vm/asdf.git "$NVM_DIR"
                ASDF_NEW=true
            fi
            cd "$ASDF_DIR"
            if [ $ASDF_NEW ]; then
                git checkout "$(git describe --abbrev=0 --tags)"
            else
                asdf update
            fi
        ) && \. "$ASDF_DIR/nvm.sh" && ([ -z "$BASH_VERSION" ] || \. "$ASDF_DIR/completions/asdf.bash")
    fi

    printf -- "%sInstalling/updating ASDF plugins...%s\n" "$BLUE" "$RESET"
    asdf plugin add golang
    asdf plugin add nodejs
    # asdf plugin add python
    asdf plugin update --all

    asdf install golang latest
    asdf install nodejs latest
}

finalize_dotfiles() {
    printf -- "\n%sFinalizing dotfiles:%s\n\n" "$BOLD" "$RESET"

    printf -- "%sUpdating dotfiles at destination...%s\n" "$BLUE" "$RESET"
    chezmoi apply
}

main() {
    printf -- "\n%sDotfiles setup script%s\n" "$BOLD" "$RESET"

    command_exists chezmoi || {
        error "chezmoi is not installed"
        exit 1
    }

    setup_dependencies
    setup_color
    setup_prompts
    setup_applications
    setup_devtools
    setup_ai_tools
    finalize_dotfiles
    setup_tmux_plugins
    setup_patched_tools

    printf -- "\n%sDone.%s\n\n" "$GREEN" "$RESET"

    # if [ -n "`$SHELL -c 'echo $ZSH_VERSION'`" ]; then
    #    [ -s "$HOME/.zshrc" ] && \. "$HOME/.zshrc"
    # elif [ -n "`$SHELL -c 'echo $BASH_VERSION'`" ]; then
    #    [ -s "$HOME/.bashrc" ] && \. "$HOME/.bashrc"
    # fi
}

main "$@"
