#!/bin/bash

# chats Quick Start Script
# This script helps you quickly set up and start the chats application

set -e

echo "================================"
echo "  chats Setup & Start Script"
echo "================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    echo "Please install Docker from https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker compose &> /dev/null; then
    echo -e "${RED}Error: Docker Compose is not installed${NC}"
    echo "Please install Docker Compose from https://docs.docker.com/compose/install/"
    exit 1
fi

echo -e "${GREEN}✓ Docker and Docker Compose are installed${NC}"
echo ""

# Check if .env files exist
if [ ! -f backend/.env ]; then
    echo -e "${YELLOW}Warning: backend/.env not found${NC}"
    echo "Creating from backend/.env.example..."
    cp backend/.env.example backend/.env
    echo -e "${YELLOW}Please edit backend/.env and add your Meta API credentials${NC}"
    echo ""
fi

if [ ! -f frontend/.env ]; then
    echo -e "${YELLOW}Warning: frontend/.env not found${NC}"
    echo "Creating from frontend/.env.example..."
    echo "VITE_API_URL=http://localhost:8000/api" > frontend/.env
    echo "VITE_WS_URL=ws://localhost:8000/ws" >> frontend/.env
    echo -e "${GREEN}✓ Created frontend/.env${NC}"
    echo ""
fi

# Check if encryption key is set
if ! grep -q "ENCRYPTION_KEY=.\+" backend/.env; then
    echo -e "${YELLOW}Generating encryption key...${NC}"
    ENCRYPTION_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())" 2>/dev/null || echo "")
    if [ -n "$ENCRYPTION_KEY" ]; then
        sed -i "s/ENCRYPTION_KEY=.*/ENCRYPTION_KEY=$ENCRYPTION_KEY/" backend/.env
        echo -e "${GREEN}✓ Encryption key generated${NC}"
    else
        echo -e "${YELLOW}Could not generate encryption key automatically${NC}"
        echo "Please run: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
        echo "And add it to backend/.env as ENCRYPTION_KEY"
    fi
    echo ""
fi

# Ask user what to do
echo "What would you like to do?"
echo "1) Start all services"
echo "2) Start services and run migrations"
echo "3) Stop all services"
echo "4) View logs"
echo "5) Rebuild and start"
echo ""
read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        echo -e "${GREEN}Starting all services...${NC}"
        docker compose up -d
        echo ""
        echo -e "${GREEN}✓ Services started successfully!${NC}"
        echo ""
        echo "Access the application at:"
        echo "  - Frontend: http://localhost:5173"
        echo "  - Backend API: http://localhost:8000/api"
        echo "  - Admin Panel: http://localhost:8000/admin"
        echo ""
        echo "View logs with: docker compose logs -f"
        ;;
    2)
        echo -e "${GREEN}Starting all services...${NC}"
        docker compose up -d

        echo ""
        echo -e "${GREEN}Waiting for database to be ready...${NC}"
        sleep 10

        echo ""
        echo -e "${GREEN}Running migrations...${NC}"
        docker compose exec backend python manage.py migrate

        echo ""
        echo -e "${YELLOW}Do you want to create a superuser? (y/n)${NC}"
        read -p "" create_superuser

        if [ "$create_superuser" = "y" ] || [ "$create_superuser" = "Y" ]; then
            docker compose exec backend python manage.py createsuperuser
        fi

        echo ""
        echo -e "${GREEN}✓ Setup completed successfully!${NC}"
        echo ""
        echo "Access the application at:"
        echo "  - Frontend: http://localhost:5173"
        echo "  - Backend API: http://localhost:8000/api"
        echo "  - Admin Panel: http://localhost:8000/admin"
        ;;
    3)
        echo -e "${YELLOW}Stopping all services...${NC}"
        docker compose down
        echo -e "${GREEN}✓ Services stopped${NC}"
        ;;
    4)
        echo -e "${GREEN}Showing logs (Ctrl+C to exit)...${NC}"
        docker compose logs -f
        ;;
    5)
        echo -e "${YELLOW}Rebuilding and starting services...${NC}"
        docker compose down
        docker compose build --no-cache
        docker compose up -d

        echo ""
        echo -e "${GREEN}Waiting for database to be ready...${NC}"
        sleep 10

        echo ""
        echo -e "${GREEN}Running migrations...${NC}"
        docker compose exec backend python manage.py migrate

        echo ""
        echo -e "${GREEN}✓ Services rebuilt and started successfully!${NC}"
        ;;
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""
echo "================================"
echo "  For more help, see:"
echo "  - README.md"
echo "  - SETUP_GUIDE.md"
echo "  - PROJECT_PLAN.md"
echo "================================"
