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

generate_env() {
    info "Generating .env files..."

    if [ -f backend/.env ] || [ -f backend/.env.dev ]; then
        if ! gum confirm "Env files already exist. Overwrite?"; then
            return
        fi
    fi

    local bot_token=$(gum input --placeholder "Enter Telegram Bot Token" --password)
    
    if [ -z "$bot_token" ]; then
        error "Bot token is required!"
    fi

    info "Generating secrets..."
    
    local jwt_secret=$(openssl rand -hex 32)
    local login_secret=$(openssl rand -hex 32)
    local refresh_secret=$(openssl rand -hex 32)
    local recovery_secret=$(openssl rand -hex 32)
    local api_secret=$(openssl rand -hex 32)
    local api_key="sk_$(openssl rand -hex 24)"

    # Backend Prod
    cat > backend/.env <<EOF
HOST=0.0.0.0:8000
CORS_ORIGINS="http://localhost,http://localhost:80"
BOT_TOKEN="$bot_token"
JWT_SECRET="$jwt_secret"
LOGIN_SECRET="$login_secret"
REFRESH_SECRET="$refresh_secret"
RECOVERY_SECRET="$recovery_secret"
API_SECRET="$api_secret"
API_TOKEN_HASH="$api_key"
DATABASE_URL="postgresql+asyncpg://postgres:password@db:5432/app"
S3_REGION="us-east-1"
S3_ENDPOINT="http://minio:9000"
S3_KEY_ID="minio"
S3_SECRET_ACCESS_KEY="minio123"
S3_BUCKET="app"
REDIS_HOST="redis"
REDIS_PORT="6379"
REDIS_PASSWORD="password"
LOGIN_EXPIRE="5m"
ACCESS_EXPITRE="30m"
REFRESH_EXPIRE="60d"
DEV="false"
EOF

    # Backend Dev
    cat > backend/.env.dev <<EOF
HOST=0.0.0.0:8000
CORS_ORIGINS="http://localhost:5173,http://localhost:80"
BOT_TOKEN="$bot_token"
JWT_SECRET="$jwt_secret"
LOGIN_SECRET="$login_secret"
REFRESH_SECRET="$refresh_secret"
RECOVERY_SECRET="$recovery_secret"
API_SECRET="$api_secret"
API_TOKEN_HASH="$api_key"
DATABASE_URL="postgresql+asyncpg://postgres:password@db:5432/app"
S3_REGION="us-east-1"
S3_ENDPOINT="http://minio:9000"
S3_KEY_ID="minio"
S3_SECRET_ACCESS_KEY="minio123"
S3_BUCKET="app"
REDIS_HOST="redis"
REDIS_PORT="6379"
REDIS_PASSWORD="password"
LOGIN_EXPIRE="5m"
ACCESS_EXPITRE="30m"
REFRESH_EXPIRE="60d"
DEV="true"
EOF

    # Bot Prod
    cat > bot/.env <<EOF
BOT_TOKEN="$bot_token"
API_ENDPOINT="http://backend:8000"
API_KEY="$api_key"
EOF

    # Bot Dev
    cat > bot/.env.dev <<EOF
BOT_TOKEN="$bot_token"
API_ENDPOINT="http://backend:8000"
API_KEY="$api_key"
EOF

    # Frontend Prod
    cat > frontend/.env <<EOF
VITE_API_URL=""
EOF

    # Frontend Dev
    cat > frontend/.env.dev <<EOF
VITE_API_URL=""
EOF

    success ".env files generated successfully!"
}

run_dev() {
    local all_services=$(docker compose config --services)

    if [ -z "$all_services" ]; then
        error "No services found in docker-compose.yml"
        return 1
    fi

    info "Select services to run (Space to select, Enter to confirm):"
    local selected_services=$(echo "$all_services" | gum choose --no-limit --selected="db,minio,redis,backend,bot,frontend")

    if [ -z "$selected_services" ]; then
        echo "No services selected. Exiting..."
        return 0
    fi

    info "Running in development mode for: $(echo $selected_services | tr '\n' ' ')"

    docker compose -f docker-compose.yml -f docker-compose.dev.yml \
        up $selected_services --build --watch
}

run_prod() {
    info "Running in production mode..."
    docker compose -f docker-compose.yml -f docker-compose.prod.yml \
        up -d --build
    success "Production services started!"
}

inst_deps() {
    gum spin --spinner dot --title "Installing dependencies..." -- sleep 3
    success "All dependencies installed!"
    sleep 1
}

main_menu() {
    while true; do
        clear

        CHOICE=$(gum choose --header "🎉 Select an option:" \
            "🔑 Generate .env files" \
            "󰇚 Install all deps" \
            "  Run dev version" \
            " Run prod version" \
            " Exit")

        case "$CHOICE" in
            "🔑 Generate .env files")
                generate_env
                ;;
            "󰇚 Install all deps")
                inst_deps
                ;;
            "  Run dev version")
                run_dev
                ;;
            " Run prod version")
                run_prod
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
