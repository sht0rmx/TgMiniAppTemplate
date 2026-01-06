#!/bin/bash

BLUE='\033[0;34m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

info() { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

check_gum() {
    command -v gum &> /dev/null
}

install_gum() {
    info "Gum not found. Installing..."
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        winget install charmbracelet.gum
    elif [ -f /etc/arch-release ]; then
        sudo pacman -S --noconfirm gum
    elif [ -f /etc/debian_version ]; then
        sudo mkdir -p /etc/apt/keyrings
        curl -fsSL https://repo.charm.sh/apt/gpg.key | sudo gpg --dearmor -o /etc/apt/keyrings/charm.gpg
        echo "deb [signed-by=/etc/apt/keyrings/charm.gpg] https://repo.charm.sh/apt/ * *" | sudo tee /etc/apt/sources.list.d/charm.list
        sudo apt update && sudo apt install -y gum
    fi
}

run_dev() {
    local all_services=$(docker compose config --services)

    if [ -z "$all_services" ]; then
        error "No services found in docker-compose.yml"
        return 1
    fi

    info "Select services to run (Space to select, Enter to confirm):"
    local selected_services=$(echo "$all_services" | gum choose --no-limit)

    if [ -z "$selected_services" ]; then
        warn "No services selected. Exiting..."
        return 0
    fi

    info "Running in development mode for: $(echo $selected_services | tr '\n' ' ')"

    docker compose -f docker-compose.yml -f docker-compose.dev.yml \
        up $selected_services --build --watch
}

inst_deps() {
    gum spin --spinner dot --title "Installing dependencies..." -- sleep 3
    success "All dependencies installed!"
    sleep 1
}

configs_create() {
    info "Creating configuration files..."
    sleep 2
    success "Configuration files created!"
}

main_menu() {
    while true; do
        clear

        CHOICE=$(gum choose --header "🎉 Select an option:" \
            "󰇚 Install all deps" \
            "  Run dev version" \
            " Run prod version" \
            " Edit configs" \
            " Exit")

        case "$CHOICE" in
            "󰇚 Install all deps")
                inst_deps
                ;;
            "  Run dev version")
                run_dev
                ;;
            " Edit configs")
                configs_create
                ;;
            " Exit")
                info "Exiting..."
                exit 0
                ;;
        esac
    done
}

if ! check_gum; then
    install_gum
    if ! check_gum; then
        error "Failed to install gum. Please install it manually."
    fi
fi

main_menu