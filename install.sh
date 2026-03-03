#!/bin/bash

# Цвета для вывода
BLUE='\033[0;34m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

info() { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# Проверка наличия gum
check_gum() {
    command -v gum &> /dev/null
}

install_gum() {
    info "Gum не найден. Установка..."
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

# Функция для безопасной генерации паролей
get_val() {
    local input=$1
    local len=$2
    if [ -z "$input" ]; then
        # Генерируем строку, удаляем спецсимволы, которые могут сломать URL (/, +, =)
        openssl rand -base64 32 | tr -d '/+=' | cut -c1-"$len"
    else
        echo "$input"
    fi
}

generate_env() {
    # ПРОВЕРКА ПЕРЕЗАПИСИ
    if [ -f .env ] || [ -f backend/.env ] || [ -f frontend/.env.dev ]; then
        echo ""
        if ! gum confirm "Файлы .env уже существуют. Перезаписать их новыми данными?"; then
            info "Операция отменена. Старые файлы сохранены."
            return
        fi
    fi

    clear
    info "--- Настройка окружения TG MiniApp ---"

    # 1. Запрос обязательных данных для PROD
    info "Настройка PRODUCTION бота:"
    local bot_token=$(gum input --placeholder "PROD Telegram Bot Token (из @BotFather)" --width 60)
    [ -z "$bot_token" ] && error "PROD Bot Token обязателен!"

    local bot_name=$(gum input --placeholder "Username PROD бота (без @)" --width 60)
    [ -z "$bot_name" ] && error "Username PROD бота обязателен!"

    # 1.1 Запрос данных для DEV
    echo ""
    info "Настройка DEVELOPMENT бота и сети (Enter = использовать данные PROD):"
    local dev_bot_token=$(gum input --placeholder "DEV Telegram Bot Token" --width 60)
    [ -z "$dev_bot_token" ] && dev_bot_token="$bot_token"

    local dev_bot_name=$(gum input --placeholder "Username DEV бота (без @)" --width 60)
    [ -z "$dev_bot_name" ] && dev_bot_name="$bot_name"

    local tunnel_url=$(gum input --placeholder "Dev Tunnel URL (например: https://xyz.ngrok.app)" --width 60)

    # 2. Запрос паролей с автогенерацией
    echo ""
    info "Настройка баз данных:"
    local raw_pg=$(gum input --placeholder "Пароль PostgreSQL (Enter = автогенерация)" --password)
    local pg_pass=$(get_val "$raw_pg" 16)

    local raw_redis=$(gum input --placeholder "Пароль Redis (Enter = автогенерация)" --password)
    local redis_pass=$(get_val "$raw_redis" 16)

    local raw_minio=$(gum input --placeholder "Пароль MinIO (Enter = автогенерация)" --password)
    local minio_pass=$(get_val "$raw_minio" 16)

    # 3. Генерация системных секретов
    info "Генерация секретных ключей..."
    local jwt_sec=$(openssl rand -hex 32)
    local log_sec=$(openssl rand -hex 32)
    local ref_sec=$(openssl rand -hex 32)
    local rec_sec=$(openssl rand -hex 32)
    local api_sec=$(openssl rand -hex 32)
    local api_key="sk_$(openssl rand -hex 24)"

    # --- ЗАПИСЬ ФАЙЛОВ ---

    # 1. ROOT .env
    cat > .env <<EOF
POSTGRES_USER="postgres"
POSTGRES_PASSWORD="$pg_pass"
POSTGRES_DB="app"
MINIO_ROOT_USER="minio"
MINIO_ROOT_PASSWORD="$minio_pass"
REDIS_PASSWORD="$redis_pass"
EOF

    # 2. BACKEND .env & .env.dev
    for mode in "env" "env.dev"; do
        local is_dev="false"
        local current_bot_token="$bot_token"
        local cors="http://localhost:5173,http://localhost:80"

        # Если генерируем DEV файл, подставляем DEV-токен и добавляем Tunnel URL в CORS
        if [[ "$mode" == "env.dev" ]]; then
            is_dev="true"
            current_bot_token="$dev_bot_token"
            if [ -n "$tunnel_url" ]; then
                cors="$cors,$tunnel_url"
            fi
        fi

        cat > "backend/.$mode" <<EOF
HOST=0.0.0.0:8000
CORS_ORIGINS="$cors"
BOT_TOKEN="$current_bot_token"
JWT_SECRET="$jwt_sec"
LOGIN_SECRET="$log_sec"
REFRESH_SECRET="$ref_sec"
RECOVERY_SECRET="$rec_sec"
API_SECRET="$api_sec"
API_TOKEN_HASH="$api_key"
DATABASE_URL="postgresql+asyncpg://postgres:$pg_pass@db:5432/app"
S3_REGION="us-east-1"
S3_ENDPOINT="http://minio:9000"
S3_KEY_ID="minio"
S3_SECRET_ACCESS_KEY="$minio_pass"
S3_BUCKET="app"
REDIS_HOST="redis"
REDIS_PORT="6379"
REDIS_PASSWORD="$redis_pass"
LOGIN_EXPIRE="5m"
ACCESS_EXPITRE="30m"
REFRESH_EXPIRE="60d"
DEV="$is_dev"
EOF
    done

    # 3. BOT .env (PROD)
    cat > bot/.env <<EOF
BOT_TOKEN="$bot_token"
API_ENDPOINT="http://backend:8000/"
API_KEY="$api_key"
TG_STARTAPP_URL="https://t.me/$bot_name?startapp"
EOF

    # 3.1 BOT .env.dev (DEV)
    cat > bot/.env.dev <<EOF
BOT_TOKEN="$dev_bot_token"
API_ENDPOINT="http://backend:8000/"
API_KEY="$api_key"
TG_STARTAPP_URL="https://t.me/$dev_bot_name?startapp"
EOF

    # 4. FRONTEND .env (PROD)
    cat > frontend/.env <<EOF
VITE_APP_TITLE="TG MiniApp"
VITE_API_URL="/"
VITE_FRONTEND_URL="http://localhost:80"
VITE_TG_MINIAPP_START="https://t.me/$bot_name?startapp"
VITE_CONSTRUCTION_MODE=""
EOF

    # 4.1 FRONTEND .env.dev (DEV)
    # Если введен туннель, фронтенд тоже должен знать свой внешний адрес
    local frontend_dev_url="http://localhost:5173"
    [ -n "$tunnel_url" ] && frontend_dev_url="$tunnel_url"

    cat > frontend/.env.dev <<EOF
VITE_APP_TITLE="TG MiniApp (Dev)"
VITE_API_URL="/"
VITE_FRONTEND_URL="$frontend_dev_url"
VITE_TG_MINIAPP_START="https://t.me/$dev_bot_name?startapp"
VITE_CONSTRUCTION_MODE=""
VITE_API_PROXY="http://backend:8000"
EOF

    success "Все .env файлы успешно созданы и синхронизированы!"
    echo -e "${BLUE}Пароль БД:${NC} $pg_pass"
    echo -e "${BLUE}Пароль Redis:${NC} $redis_pass"
    echo -e "${BLUE}Пароль MinIO:${NC} $minio_pass"
    echo -e "${BLUE}CORS (Dev):${NC} Установлен с поддержкой Tunnel"
    sleep 3
}
check_tool() {
    local tool=$1
    local name=$2
    if command -v "$tool" &> /dev/null; then
        echo -e "  ${GREEN}✓${NC} $name установлен ($( "$tool" --version | head -n 1 ))"
        return 0
    else
        echo -e "  ${RED}✗${NC} $name не найден"
        return 1
    fi
}

inst_deps() {
    clear
    info "Проверка системных зависимостей..."
    echo "--------------------------------"

    local missing=0

    # Проверка Docker
    check_tool "docker" "Docker" || ((missing++))
    check_tool "docker-compose" "Docker Compose" || {
        # Проверка нового синтаксиса 'docker compose'
        if docker compose version &> /dev/null; then
            echo -e "  ${GREEN}✓${NC} Docker Compose (v2 plugin)"
        else
            ((missing++))
        fi
    }

    # Проверка Node.js среды
    check_tool "node" "Node.js" || ((missing++))
    check_tool "npm" "NPM" || ((missing++))

    # Проверка Python среды
    check_tool "python3" "Python 3" || ((missing++))
    check_tool "uv" "UV (Python Package Manager)" || {
        echo -e "${BLUE}[HINT]${NC} Рекомендуется установить 'uv' для быстрого бэкенда: curl -LsSf https://astral.sh/uv/install.sh | sh"
        ((missing++))
    }

    echo "--------------------------------"

    if [ $missing -eq 0 ]; then
        success "Все зависимости найдены! Вы готовы к работе."
    else
        echo -e "${RED}[ВНИМАНИЕ]${NC} Отсутствует инструментов: $missing"
        echo "Пожалуйста, установите недостающие компоненты для корректной работы."
    fi

    # Даем пользователю время прочитать результат
    echo ""
    read -p "Нажмите Enter, чтобы вернуться в меню..."
}
run_dev() {
    info "Запуск в режиме разработки..."
    docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build --watch
}

run_prod() {
    info "Запуск в продакшн..."
    docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
    success "Сервисы запущены в фоне!"
}

main_menu() {
    while true; do
        clear
        CHOICE=$(gum choose --header "🚀 Панель управления проектом:" \
            "🔑 Сгенерировать .env файлы" \
            "󰇚 Установить зависимости" \
            "  Запустить DEV версию" \
            " Запустить PROD версию" \
            " Выход")

        case "$CHOICE" in
            "🔑 Сгенерировать .env файлы") generate_env ;;
            "󰇚 Установить зависимости") inst_deps ;;
            "  Запустить DEV версию") run_dev ;;
            " Запустить PROD версию") run_prod ;;
            " Выход") exit 0 ;;
        esac
    done
}

# Старт скрипта
if ! check_gum; then
    install_gum
fi

main_menu