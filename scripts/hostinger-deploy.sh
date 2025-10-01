#!/bin/bash

# Hostinger Deployment Script for Pet Automation Suite
# This script deploys the application to Hostinger VPS/Shared Hosting

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DEPLOY_USER="${DEPLOY_USER:-$(whoami)}"
DEPLOY_PATH="${DEPLOY_PATH:-/home/$DEPLOY_USER/pet-automation}"
PYTHON_VERSION="3.11"
PORT="${PORT:-8000}"

# Functions
print_header() {
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════════════════════════════════╗"
    echo "║         Pet Automation Suite - Hostinger Deployment               ║"
    echo "╚════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

check_requirements() {
    print_info "Checking system requirements..."
    
    # Check Python version
    if command -v python3.11 &> /dev/null; then
        print_success "Python 3.11 found"
    elif command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
        if [ "$PYTHON_VERSION" == "3.11" ] || [ "$PYTHON_VERSION" == "3.10" ] || [ "$PYTHON_VERSION" == "3.9" ]; then
            print_success "Python $PYTHON_VERSION found (compatible)"
        else
            print_error "Python 3.9+ required. Found: $PYTHON_VERSION"
            exit 1
        fi
    else
        print_error "Python not found. Please install Python 3.11"
        exit 1
    fi
    
    # Check pip
    if command -v pip3 &> /dev/null; then
        print_success "pip3 found"
    else
        print_error "pip3 not found. Please install pip3"
        exit 1
    fi
    
    # Check git
    if command -v git &> /dev/null; then
        print_success "git found"
    else
        print_warning "git not found. Some features may not work"
    fi
}

setup_directories() {
    print_info "Setting up directories..."
    
    # Create deployment directory
    mkdir -p "$DEPLOY_PATH"
    mkdir -p "$DEPLOY_PATH/logs"
    mkdir -p "$DEPLOY_PATH/data"
    mkdir -p "$DEPLOY_PATH/backups"
    mkdir -p "$DEPLOY_PATH/config"
    
    print_success "Directories created"
}

backup_current_deployment() {
    if [ -d "$DEPLOY_PATH/current" ]; then
        print_info "Backing up current deployment..."
        
        BACKUP_NAME="backup_$(date +%Y%m%d_%H%M%S)"
        mv "$DEPLOY_PATH/current" "$DEPLOY_PATH/backups/$BACKUP_NAME"
        
        # Keep only last 5 backups
        cd "$DEPLOY_PATH/backups"
        ls -t | tail -n +6 | xargs -r rm -rf
        
        print_success "Backup created: $BACKUP_NAME"
    fi
}

deploy_application() {
    print_info "Deploying application..."
    
    # Create new deployment directory
    mkdir -p "$DEPLOY_PATH/current"
    
    # Copy files
    print_info "Copying application files..."
    rsync -av --exclude='.git' \
              --exclude='__pycache__' \
              --exclude='*.pyc' \
              --exclude='venv' \
              --exclude='logs' \
              --exclude='.env' \
              "$PROJECT_ROOT/" "$DEPLOY_PATH/current/"
    
    print_success "Files copied"
}

setup_virtual_environment() {
    print_info "Setting up virtual environment..."
    
    cd "$DEPLOY_PATH/current"
    
    # Create virtual environment
    python3 -m venv venv
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install dependencies
    print_info "Installing dependencies..."
    pip install -r requirements.txt
    
    print_success "Virtual environment ready"
}

setup_environment_variables() {
    print_info "Setting up environment variables..."
    
    if [ ! -f "$DEPLOY_PATH/.env" ]; then
        print_warning ".env file not found. Creating from template..."
        
        # Copy example env file
        cp "$DEPLOY_PATH/current/.env.example" "$DEPLOY_PATH/.env"
        
        # Generate secret key
        SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
        sed -i "s/your_secret_key_here/$SECRET_KEY/g" "$DEPLOY_PATH/.env"
        
        print_warning "Please edit $DEPLOY_PATH/.env with your API keys"
        print_warning "Press Enter to continue after editing..."
        read
    fi
    
    # Copy .env to current deployment
    cp "$DEPLOY_PATH/.env" "$DEPLOY_PATH/current/.env"
    
    print_success "Environment variables configured"
}

initialize_database() {
    print_info "Initializing database..."
    
    cd "$DEPLOY_PATH/current"
    source venv/bin/activate
    
    # Run database initialization
    python3 << EOF
from src.models import create_database, create_session
from config.config import Config
import os

try:
    config = Config()
    engine = create_database(config.DATABASE_URL)
    session = create_session(engine)
    print("Database initialized successfully")
except Exception as e:
    print(f"Database initialization error: {e}")
    print("This is normal if database already exists")
EOF
    
    print_success "Database ready"
}

setup_systemd_service() {
    print_info "Setting up systemd service..."
    
    # Check if we have systemd access
    if [ ! -d "/etc/systemd/system" ]; then
        print_warning "systemd not available. Skipping service setup"
        return
    fi
    
    # Create systemd service file
    sudo tee /etc/systemd/system/pet-automation.service > /dev/null << EOF
[Unit]
Description=Pet Automation Suite
After=network.target

[Service]
Type=simple
User=$DEPLOY_USER
WorkingDirectory=$DEPLOY_PATH/current
Environment="PATH=$DEPLOY_PATH/current/venv/bin"
ExecStart=$DEPLOY_PATH/current/venv/bin/gunicorn --bind 0.0.0.0:$PORT --workers 4 --timeout 120 src.dashboard.app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    # Create celery worker service
    sudo tee /etc/systemd/system/pet-automation-worker.service > /dev/null << EOF
[Unit]
Description=Pet Automation Suite - Celery Worker
After=network.target

[Service]
Type=simple
User=$DEPLOY_USER
WorkingDirectory=$DEPLOY_PATH/current
Environment="PATH=$DEPLOY_PATH/current/venv/bin"
ExecStart=$DEPLOY_PATH/current/venv/bin/celery -A src.celery_app worker --loglevel=info
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    # Reload systemd
    sudo systemctl daemon-reload
    
    print_success "Systemd services created"
}

start_services() {
    print_info "Starting services..."
    
    cd "$DEPLOY_PATH/current"
    source venv/bin/activate
    
    # Check if systemd is available
    if systemctl --version &> /dev/null; then
        # Use systemd
        sudo systemctl enable pet-automation
        sudo systemctl enable pet-automation-worker
        sudo systemctl restart pet-automation
        sudo systemctl restart pet-automation-worker
        
        print_success "Services started with systemd"
    else
        # Use manual process management
        print_info "Starting services manually..."
        
        # Kill old processes
        pkill -f "gunicorn.*pet-automation" || true
        pkill -f "celery.*pet-automation" || true
        
        # Start gunicorn
        nohup gunicorn --bind 0.0.0.0:$PORT --workers 4 --timeout 120 src.dashboard.app:app > "$DEPLOY_PATH/logs/gunicorn.log" 2>&1 &
        echo $! > "$DEPLOY_PATH/gunicorn.pid"
        
        # Start celery worker
        nohup celery -A src.celery_app worker --loglevel=info > "$DEPLOY_PATH/logs/celery.log" 2>&1 &
        echo $! > "$DEPLOY_PATH/celery.pid"
        
        print_success "Services started manually"
    fi
}

setup_nginx() {
    print_info "Setting up Nginx configuration..."
    
    # Check if nginx is available
    if ! command -v nginx &> /dev/null; then
        print_warning "Nginx not found. Skipping nginx setup"
        return
    fi
    
    # Create nginx config
    sudo tee /etc/nginx/sites-available/pet-automation > /dev/null << EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:$PORT;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static/ {
        alias $DEPLOY_PATH/current/src/dashboard/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF
    
    # Enable site
    sudo ln -sf /etc/nginx/sites-available/pet-automation /etc/nginx/sites-enabled/
    
    # Test nginx config
    sudo nginx -t
    
    # Reload nginx
    sudo systemctl reload nginx
    
    print_success "Nginx configured"
}

create_restart_script() {
    print_info "Creating restart script..."
    
    cat > "$DEPLOY_PATH/restart.sh" << 'EOF'
#!/bin/bash

DEPLOY_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Restarting Pet Automation Suite..."

if systemctl --version &> /dev/null; then
    # Use systemd
    sudo systemctl restart pet-automation
    sudo systemctl restart pet-automation-worker
    echo "Services restarted with systemd"
else
    # Manual restart
    cd "$DEPLOY_PATH/current"
    
    # Kill old processes
    if [ -f "$DEPLOY_PATH/gunicorn.pid" ]; then
        kill $(cat "$DEPLOY_PATH/gunicorn.pid") 2>/dev/null || true
    fi
    if [ -f "$DEPLOY_PATH/celery.pid" ]; then
        kill $(cat "$DEPLOY_PATH/celery.pid") 2>/dev/null || true
    fi
    
    # Wait for processes to stop
    sleep 2
    
    # Start new processes
    source venv/bin/activate
    
    nohup gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 120 src.dashboard.app:app > "$DEPLOY_PATH/logs/gunicorn.log" 2>&1 &
    echo $! > "$DEPLOY_PATH/gunicorn.pid"
    
    nohup celery -A src.celery_app worker --loglevel=info > "$DEPLOY_PATH/logs/celery.log" 2>&1 &
    echo $! > "$DEPLOY_PATH/celery.pid"
    
    echo "Services restarted manually"
fi

echo "Restart complete!"
EOF
    
    chmod +x "$DEPLOY_PATH/restart.sh"
    
    print_success "Restart script created"
}

verify_deployment() {
    print_info "Verifying deployment..."
    
    # Wait for services to start
    sleep 5
    
    # Check if application is responding
    if curl -f http://localhost:$PORT/health &> /dev/null; then
        print_success "Application is responding"
    else
        print_warning "Application health check failed. Check logs for details."
    fi
    
    # Check logs
    if [ -f "$DEPLOY_PATH/logs/gunicorn.log" ]; then
        print_info "Last 10 lines of gunicorn log:"
        tail -n 10 "$DEPLOY_PATH/logs/gunicorn.log"
    fi
}

generate_deployment_report() {
    print_info "Generating deployment report..."
    
    cat > "$DEPLOY_PATH/deployment_report.txt" << EOF
Pet Automation Suite - Deployment Report
========================================
Date: $(date)
Deployment Path: $DEPLOY_PATH
Port: $PORT
Python Version: $(python3 --version)

Services Status:
EOF
    
    if systemctl --version &> /dev/null; then
        echo "Main Service: $(systemctl is-active pet-automation)" >> "$DEPLOY_PATH/deployment_report.txt"
        echo "Worker Service: $(systemctl is-active pet-automation-worker)" >> "$DEPLOY_PATH/deployment_report.txt"
    else
        echo "Main Service: Running (PID: $(cat $DEPLOY_PATH/gunicorn.pid 2>/dev/null || echo 'N/A'))" >> "$DEPLOY_PATH/deployment_report.txt"
        echo "Worker Service: Running (PID: $(cat $DEPLOY_PATH/celery.pid 2>/dev/null || echo 'N/A'))" >> "$DEPLOY_PATH/deployment_report.txt"
    fi
    
    cat >> "$DEPLOY_PATH/deployment_report.txt" << EOF

Access Information:
- Dashboard: http://localhost:$PORT
- Health Check: http://localhost:$PORT/health
- Logs: $DEPLOY_PATH/logs/

Next Steps:
1. Configure your API keys in $DEPLOY_PATH/.env
2. Set up a domain name and SSL certificate
3. Configure firewall rules to allow port $PORT
4. Set up monitoring and alerts
5. Configure automated backups

Useful Commands:
- Restart services: bash $DEPLOY_PATH/restart.sh
- View logs: tail -f $DEPLOY_PATH/logs/gunicorn.log
- Check status: systemctl status pet-automation (if using systemd)

Support:
- Check logs in $DEPLOY_PATH/logs/
- Review deployment documentation
- Contact support team
EOF
    
    print_success "Deployment report generated: $DEPLOY_PATH/deployment_report.txt"
}

main() {
    print_header
    
    # Check if running as root
    if [ "$EUID" -eq 0 ]; then
        print_warning "Running as root. It's recommended to run as a regular user."
        read -p "Continue anyway? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    # Run deployment steps
    check_requirements
    setup_directories
    backup_current_deployment
    deploy_application
    setup_virtual_environment
    setup_environment_variables
    initialize_database
    setup_systemd_service
    start_services
    setup_nginx
    create_restart_script
    verify_deployment
    generate_deployment_report
    
    print_success "Deployment completed successfully!"
    print_info "Access your application at: http://localhost:$PORT"
    print_info "Check the deployment report at: $DEPLOY_PATH/deployment_report.txt"
}

# Run main function
main "$@"