#!/bin/bash

# Django AdminLTE Docker Deployment Script for Ubuntu
# This script sets up and deploys the Django application on Ubuntu with SSL

set -e

echo "🚀 Starting Django AdminLTE deployment for exmanager.flimboo.com..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "Run: sudo apt update && sudo apt install docker.io docker-compose"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "Run: sudo apt install docker-compose"
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env.production .env
    echo "⚠️  Please edit .env file with your production settings before continuing!"
    echo "   - Change SECRET_KEY to a secure value"
    echo "   - Verify ALLOWED_HOSTS includes exmanager.flimboo.com"
    echo "   - Verify CSRF_TRUSTED_ORIGINS includes https://exmanager.flimboo.com"
    read -p "Press Enter after editing .env file..."
fi

# Create media directory if it doesn't exist
mkdir -p media

# Create SSL directory for nginx
mkdir -p nginx/ssl

# Check if SSL certificates exist
if [ ! -f nginx/ssl/cert.pem ] || [ ! -f nginx/ssl/key.pem ]; then
    echo "🔐 SSL certificates not found. Setting up SSL..."
    chmod +x ssl-setup.sh
    ./ssl-setup.sh
fi

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Build and start the application
echo "🔨 Building and starting containers..."
docker-compose up --build -d

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
sleep 10

# Run migrations
echo "🗄️  Running database migrations..."
docker-compose exec appseed-app python manage.py migrate

# Create superuser if needed
echo "👤 Do you want to create a superuser? (y/n)"
read -p "Create superuser? " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker-compose exec appseed-app python manage.py createsuperuser
fi

# Collect static files
echo "📦 Collecting static files..."
docker-compose exec appseed-app python manage.py collectstatic --noinput

echo "✅ Deployment completed successfully!"
echo ""
echo "🌐 Your application is now running at:"
echo "   - HTTPS: https://exmanager.flimboo.com"
echo "   - Admin: https://exmanager.flimboo.com/admin"
echo ""
echo "📊 Container status:"
docker-compose ps
echo ""
echo "📝 Useful commands:"
echo "   - View logs: docker-compose logs -f"
echo "   - Stop: docker-compose down"
echo "   - Restart: docker-compose restart"
echo "   - Update: git pull && docker-compose up --build -d"
echo "   - SSL renewal: ./ssl-setup.sh" 