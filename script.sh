#!/usr/bin/env bash
set -e

APP_NAME="marzneshiniplimit"
CONFIG_DIR="/opt/$APP_NAME"
COMPOSE_FILE="$CONFIG_DIR/docker-compose.yml"

FETCH_REPO="jenaze/MarzneshinIpLimit"
SCRIPT_URL="https://github.com/$FETCH_REPO/raw/main/script.sh"

colorized_echo() {
    local color=$1
    local text=$2

    case $color in
        "red")
        printf "\e[91m${text}\e[0m\n";;
        "green")
        printf "\e[92m${text}\e[0m\n";;
        "yellow")
        printf "\e[93m${text}\e[0m\n";;
        "blue")
        printf "\e[94m${text}\e[0m\n";;
        "magenta")
        printf "\e[95m${text}\e[0m\n";;
        "cyan")
        printf "\e[96m${text}\e[0m\n";;
        *)
            echo "${text}"
        ;;
    esac
}


check_running_as_root() {
    if [ "$(id -u)" != "0" ]; then
        colorized_echo red "This command must be run as root."
        exit 1
    fi
}

detect_os() {
    # Detect the operating system
    if [ -f /etc/lsb-release ]; then
        OS=$(lsb_release -si)
        elif [ -f /etc/os-release ]; then
        OS=$(awk -F= '/^NAME/{print $2}' /etc/os-release | tr -d '"')
        elif [ -f /etc/redhat-release ]; then
        OS=$(cat /etc/redhat-release | awk '{print $1}')
        elif [ -f /etc/arch-release ]; then
        OS="Arch"
    else
        colorized_echo red "Unsupported operating system"
        exit 1
    fi
}

detect_and_update_package_manager() {
    colorized_echo blue "Updating package manager"
    if [[ "$OS" == "Ubuntu"* ]] || [[ "$OS" == "Debian"* ]]; then
        PKG_MANAGER="apt-get"
        $PKG_MANAGER update
        elif [[ "$OS" == "CentOS"* ]] || [[ "$OS" == "AlmaLinux"* ]]; then
        PKG_MANAGER="yum"
        $PKG_MANAGER update -y
        $PKG_MANAGER install -y epel-release
        elif [ "$OS" == "Fedora"* ]; then
        PKG_MANAGER="dnf"
        $PKG_MANAGER update
        elif [ "$OS" == "Arch" ]; then
        PKG_MANAGER="pacman"
        $PKG_MANAGER -Sy
    else
        colorized_echo red "Unsupported operating system"
        exit 1
    fi
}

detect_compose() {
    # Check if docker compose command exists
    if docker compose >/dev/null 2>&1; then
        COMPOSE='docker compose'
        elif docker-compose >/dev/null 2>&1; then
        COMPOSE='docker-compose'
    else
        colorized_echo red "docker compose not found"
        exit 1
    fi
}

install_package () {
    if [ -z $PKG_MANAGER ]; then
        detect_and_update_package_manager
    fi

    PACKAGE=$1
    colorized_echo blue "Installing $PACKAGE"
    if [[ "$OS" == "Ubuntu"* ]] || [[ "$OS" == "Debian"* ]]; then
        $PKG_MANAGER -y install "$PACKAGE"
        elif [[ "$OS" == "CentOS"* ]] || [[ "$OS" == "AlmaLinux"* ]]; then
        $PKG_MANAGER install -y "$PACKAGE"
        elif [ "$OS" == "Fedora"* ]; then
        $PKG_MANAGER install -y "$PACKAGE"
        elif [ "$OS" == "Arch" ]; then
        $PKG_MANAGER -S --noconfirm "$PACKAGE"
    else
        colorized_echo red "Unsupported operating system"
        exit 1
    fi
}

install_docker() {
    # Install Docker and Docker Compose using the official installation script
    colorized_echo blue "Installing Docker"
    curl -fsSL https://get.docker.com | sh
    colorized_echo green "Docker installed successfully"
}

install_marzneshin_ip_limit_script() {
    colorized_echo blue "Installing marzneshiniplimit script"
    curl -sSL $SCRIPT_URL | install -m 755 /dev/stdin /usr/local/bin/marzneshiniplimit
    colorized_echo green "marzneshiniplimit script installed successfully"
}

install_marzneshin_ip_limit() {
    # Fetch releases
    FILES_URL_PREFIX="https://raw.githubusercontent.com/jenaze/MarzneshinIpLimit/main"
	COMPOSE_FILES_URL="https://raw.githubusercontent.com/jenaze/MarzneshinIpLimit/main"
  
    mkdir -p "$CONFIG_DIR"

    colorized_echo blue "Fetching compose file"
    curl -sL "$COMPOSE_FILES_URL/docker-compose.yml" -o "$CONFIG_DIR/docker-compose.yml"
    colorized_echo green "File saved in $CONFIG_DIR/docker-compose.yml"
	
    colorized_echo blue "Fetching config.json file"
    curl -sL "$FILES_URL_PREFIX/config.json.example" -o "$CONFIG_DIR/config.json"
    colorized_echo green "File saved in $CONFIG_DIR/config.json"

    colorized_echo blue "Creating app.log file"
    touch "$CONFIG_DIR/app.log"
    colorized_echo green "File created in $CONFIG_DIR/config.json"

    colorized_echo green "MarzneshinIpLimit files downloaded successfully"
}

uninstall_marzneshin_ip_limit_script() {
    if [ -f "/usr/local/bin/marzneshiniplimit" ]; then
        colorized_echo yellow "Removing marzneshiniplimit script"
        rm "/usr/local/bin/marzneshiniplimit"
    fi
}

uninstall_marzneshin_ip_limit() {
    if [ -d "$CONFIG_DIR" ]; then
        colorized_echo yellow "Removing directory: $CONFIG_DIR"
        rm -r "$CONFIG_DIR"
    fi
}

uninstall_marzneshin_ip_limit_docker_images() {
    images=$(docker images | grep marzneshiniplimit | awk '{print $3}')

    if [ -n "$images" ]; then
        colorized_echo yellow "Removing Docker images of Marzneshin Ip Limit"
        for image in $images; do
            if docker rmi "$image" >/dev/null 2>&1; then
                colorized_echo yellow "Image $image removed"
            fi
        done
    fi
}

up_marzneshin_ip_limit() {
    $COMPOSE -f $COMPOSE_FILE -p "$APP_NAME" up -d --remove-orphans
}

down_marzneshin_ip_limit() {
    $COMPOSE -f $COMPOSE_FILE -p "$APP_NAME" down
}

show_marzneshin_ip_limit_logs() {
    $COMPOSE -f $COMPOSE_FILE -p "$APP_NAME" logs
}

follow_marzneshin_ip_limit_logs() {
    $COMPOSE -f $COMPOSE_FILE -p "$APP_NAME" logs -f
}


update_marzneshin_ip_limit_script() {
    colorized_echo blue "Updating marzneshiniplimit script"
    curl -sSL $SCRIPT_URL | install -m 755 /dev/stdin /usr/local/bin/marzneshiniplimit
    colorized_echo green "marzneshiniplimit script updated successfully"
}

update_marzneshin_ip_limit() {
    $COMPOSE -f $COMPOSE_FILE -p "$APP_NAME" pull
}

is_marzneshin_ip_limit_installed() {
    if [ -d $CONFIG_DIR ]; then
        return 0
    else
        return 1
    fi
}

is_marzneshin_ip_limit_up() {
    if [ -z "$($COMPOSE -f $COMPOSE_FILE ps -q -a)" ]; then
        return 1
    else
        return 0
    fi
}

install_command() {
    check_running_as_root
    # Check if marzneshin ip limit is already installed
    if is_marzneshin_ip_limit_installed; then
        colorized_echo red "MarzneshinIpLimit is already installed at $CONFIG_DIR"
        read -p "Do you want to override the previous installation? (y/n) "
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            colorized_echo red "Aborted installation"
            exit 1
        fi
    fi
    detect_os
    if ! command -v jq >/dev/null 2>&1; then
        install_package jq
    fi
    if ! command -v curl >/dev/null 2>&1; then
        install_package curl
    fi
    if ! command -v docker >/dev/null 2>&1; then
        install_docker
    fi
	
    detect_compose
    install_marzneshin_ip_limit_script
    install_marzneshin_ip_limit
    create_or_update_token
    create_or_update_admins
    update_panel
    up_marzneshin_ip_limit
    colorized_echo green "Adjust other configurations from the telegram bot"
    follow_marzneshin_ip_limit_logs
}

uninstall_command() {
    check_running_as_root
    # Check if marzneshin ip limit is installed
    if ! is_marzneshin_ip_limit_installed; then
        colorized_echo red "MarzneshinIpLimit's not installed!"
        exit 1
    fi

    read -p "Do you really want to uninstall MarzneshinIpLimit? (y/n) "
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        colorized_echo red "Aborted"
        exit 1
    fi

    detect_compose
    if is_marzneshin_ip_limit_up; then
        down_marzneshin_ip_limit
    fi
    uninstall_marzneshin_ip_limit_script
    uninstall_marzneshin_ip_limit
    uninstall_marzneshin_ip_limit_docker_images

    colorized_echo green "Marzneshin uninstalled successfully"
}

up_command() {
    help() {
        colorized_echo red "Usage: $0 up [options]"
        echo ""
        echo "OPTIONS:"
        echo "  -h, --help        display this help message"
        echo "  -n, --no-logs     do not follow logs after starting"
    }

    local no_logs=false
    while [[ "$#" -gt 0 ]]; do
        case "$1" in
            -n|--no-logs)
                no_logs=true
            ;;
            -h|--help)
                help
                exit 0
            ;;
            *)
                echo "Error: Invalid option: $1" >&2
                help
                exit 0
            ;;
        esac
        shift
    done

    # Check if marzneshin ip limit is installed
    if ! is_marzneshin_ip_limit_installed; then
        colorized_echo red "MarzneshinIpLimit is not installed!"
        exit 1
    fi

    detect_compose

    if is_marzneshin_ip_limit_up; then
        colorized_echo red "MarzneshinIpLimit is already up"
        exit 1
    fi

    up_marzneshin_ip_limit
    if [ "$no_logs" = false ]; then
        follow_marzneshin_ip_limit_logs
    fi
}

down_command() {

    # Check if marzneshin ip limit is installed
    if ! is_marzneshin_ip_limit_installed; then
        colorized_echo red "MarzneshinIpLimit's not installed!"
        exit 1
    fi

    detect_compose

    if ! is_marzneshin_ip_limit_up; then
        colorized_echo red "MarzneshinIpLimit's already down"
        exit 1
    fi

    down_marzneshin_ip_limit
}

restart_command() {
    help() {
        colorized_echo red "Usage: $0 restart [options]"
        echo
        echo "OPTIONS:"
        echo "  -h, --help        display this help message"
        echo "  -n, --no-logs     do not follow logs after starting"
    }

    local no_logs=false
    while [[ "$#" -gt 0 ]]; do
        case "$1" in
            -n|--no-logs)
                no_logs=true
            ;;
            -h|--help)
                help
                exit 0
            ;;
            *)
                echo "Error: Invalid option: $1" >&2
                help
                exit 0
            ;;
        esac
        shift
    done

    # Check if marzneshin ip limit is installed
    if ! is_marzneshin_ip_limit_installed; then
        colorized_echo red "MarzneshinIpLimit's not installed!"
        exit 1
    fi

    detect_compose

    down_marzneshin_ip_limit
    up_marzneshin_ip_limit
    if [ "$no_logs" = false ]; then
        follow_marzneshin_ip_limit_logs
    fi
}

status_command() {

    # Check if marzneshin ip limit is installed
    if ! is_marzneshin_ip_limit_installed; then
        echo -n "Status: "
        colorized_echo red "Not Installed"
        exit 1
    fi

    detect_compose

    if ! is_marzneshin_ip_limit_up; then
        echo -n "Status: "
        colorized_echo blue "Down"
        exit 1
    fi

    echo -n "Status: "
    colorized_echo green "Up"

    json=$($COMPOSE -f $COMPOSE_FILE ps -a --format=json)
    services=$(echo "$json" | jq -r 'if type == "array" then .[] else . end | .Service')
    states=$(echo "$json" | jq -r 'if type == "array" then .[] else . end | .State')
    # Print out the service names and statuses
    for i in $(seq 0 $(expr $(echo $services | wc -w) - 1)); do
        service=$(echo $services | cut -d' ' -f $(expr $i + 1))
        state=$(echo $states | cut -d' ' -f $(expr $i + 1))
        echo -n "- $service: "
        if [ "$state" == "running" ]; then
            colorized_echo green $state
        else
            colorized_echo red $state
        fi
    done
}

logs_command() {
    help() {
        colorized_echo red "Usage: marzneshin ip limit logs [options]"
        echo ""
        echo "OPTIONS:"
        echo "  -h, --help        display this help message"
        echo "  -n, --no-follow   do not show follow logs"
    }

    local no_follow=false
    while [[ "$#" -gt 0 ]]; do
        case "$1" in
            -n|--no-follow)
                no_follow=true
            ;;
            -h|--help)
                help
                exit 0
            ;;
            *)
                echo "Error: Invalid option: $1" >&2
                help
                exit 0
            ;;
        esac
        shift
    done

    # Check if marzneshin ip limit is installed
    if ! is_marzneshin_ip_limit_installed; then
        colorized_echo red "MarzneshinIpLimit is not installed!"
        exit 1
    fi

    detect_compose

    if ! is_marzneshin_ip_limit_up; then
        colorized_echo red "MarzneshinIpLimit is not up."
        exit 1
    fi

    if [ "$no_follow" = true ]; then
        tail -n 50 "$CONFIG_DIR/app.log"
    else
        tail -n 100 -f "$CONFIG_DIR/app.log"
    fi
}

update_command() {
    check_running_as_root
    # Check if marzneshin ip limit is installed
    if ! is_marzneshin_ip_limit_installed; then
        colorized_echo red "MarzneshinIpLimit is not installed!"
        exit 1
    fi

    detect_compose

    update_marzneshin_ip_limit_script
    colorized_echo blue "Pulling latest version"
    update_marzneshin_ip_limit

    colorized_echo blue "Restarting MarzneshinIpLimit's services"
    down_marzneshin_ip_limit
    up_marzneshin_ip_limit

    colorized_echo blue "MarzneshinIpLimit updated successfully"
}

create_or_update_token() {
    local token
    local confirm

    if [ -f "$CONFIG_DIR/config.json" ]; then
        token=$(jq -r '.BOT_TOKEN' "$CONFIG_DIR/config.json")
        echo "Current BOT_TOKEN is: $token"
    fi

    echo "You must create a bot and get the token, you can get it from @BotFather in Telegram."
    read -p "Enter new BOT_TOKEN: " token

    if [ -f "$CONFIG_DIR/config.json" ]; then
        jq --arg token "$token" '.BOT_TOKEN = $token' "$CONFIG_DIR/config.json" >tmp.json && mv tmp.json "$CONFIG_DIR/config.json"
    else
        echo "{\"BOT_TOKEN\": \"$token\"}" >"$CONFIG_DIR/config.json"
    fi

    echo "The BOT_TOKEN has been updated."
    echo "To apply the changes, you need to restart the program."
}

create_or_update_admins() {
    local admin
    local confirm

    if [ -f "$CONFIG_DIR/config.json" ]; then
        admin=$(jq -r '.ADMINS' "$CONFIG_DIR/config.json")
        echo "Current ADMIN is: $admin"
    fi

    echo "You must set your chat ID, you can get it from @userinfobot in Telegram."
    echo "Enter the chat ID of the admin."
    read -p "Enter new ADMIN: " admin

    if [ -f "$CONFIG_DIR/config.json" ]; then
        jq --arg admin "$admin" '.ADMINS = [$admin | tonumber]' "$CONFIG_DIR/config.json" >tmp.json && mv tmp.json "$CONFIG_DIR/config.json"
    else
        echo "{\"ADMINS\": [$admin]}" >"$CONFIG_DIR/config.json"
    fi

    echo "The ADMIN has been updated."
}

update_panel() {
    local address
    local username
    local pass
    local confirm

    if [ -f "$CONFIG_DIR/config.json" ]; then
        address=$(jq -r '.PANEL_DOMAIN' "$CONFIG_DIR/config.json")
        echo "Current panel address is: $address"
    fi

    echo "\n"
    echo "Address must not have http or https like: sub.example.ir:8080"
    read -p "Enter new panel address: " address
    read -p "Enter new panel username: " username
    read -p "Enter new panel password: " pass

    if [ -f "$CONFIG_DIR/config.json" ]; then
        jq --arg address "$address" '.PANEL_DOMAIN = $address' "$CONFIG_DIR/config.json" >tmp.json && mv tmp.json "$CONFIG_DIR/config.json"
        jq --arg username "$username" '.PANEL_USERNAME = $username' "$CONFIG_DIR/config.json" >tmp.json && mv tmp.json "$CONFIG_DIR/config.json"
        jq --arg pass "$pass" '.PANEL_PASSWORD = $pass' "$CONFIG_DIR/config.json" >tmp.json && mv tmp.json "$CONFIG_DIR/config.json"
    else
        echo "{\"ADMINS\": [$admin]}" >"$CONFIG_DIR/config.json"
    fi

    echo "The ADMIN has been updated."
}


usage() {
    colorized_echo red "Usage: $0 [command]"
    echo
    echo "Commands:"
    echo "  up              Start services"
    echo "  down            Stop services"
    echo "  restart         Restart services"
    echo "  status          Show status"
    echo "  logs            Show logs"
    echo "  token           Set telegram bot token"
    echo "  admins          Set telegram admins"
    echo "  install         Install MarzneshinIpLimit"
    echo "  update          Update latest version"
    echo "  uninstall       Uninstall MarzneshinIpLimit"
    echo "  install-script  Install MarzneshinIpLimit script"
    echo
}

case "$1" in
    up)
    shift; up_command "$@";;
    down)
    shift; down_command "$@";;
    restart)
    shift; restart_command "$@";;
    status)
    shift; status_command "$@";;
    logs)
    shift; logs_command "$@";;
    token)
    shift; create_or_update_token "$@";;
    admins)
    shift; create_or_update_admins "$@";;
    install)
    shift; install_command "$@";;
    update)
    shift; update_command "$@";;
    uninstall)
    shift; uninstall_command "$@";;
    install-script)
    shift; install_marzneshin_ip_limit_script "$@";;
    *)
    usage;;
esac
