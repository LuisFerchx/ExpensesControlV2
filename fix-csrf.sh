#!/bin/bash

# CSRF Fix Script for HTTPS Migration
# This script fixes CSRF issues when migrating from HTTP to HTTPS

set -e

echo "🔧 Fixing CSRF issues for HTTPS migration..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env.production .env
    echo "⚠️  Please edit .env file with your production settings!"
    echo "   - Change SECRET_KEY to a secure value"
    read -p "Press Enter after editing .env file..."
fi

# Stop containers
echo "🛑 Stopping containers..."
docker-compose down

# Clear browser cache and cookies (instructions)
echo "🧹 Browser Cache Instructions:"
echo "   - Clear browser cache and cookies"
echo "   - On iPhone: Settings > Safari > Clear History and Website Data"
echo "   - On Android: Chrome > Settings > Privacy and security > Clear browsing data"

# Rebuild and restart with new configuration
echo "🔨 Rebuilding containers with new CSRF configuration..."
docker-compose up --build -d

# Wait for containers to be ready
echo "⏳ Waiting for containers to be ready..."
sleep 10

# Run migrations
echo "🗄️  Running migrations..."
docker-compose exec appseed-app python manage.py migrate

# Collect static files
echo "📦 Collecting static files..."
docker-compose exec appseed-app python manage.py collectstatic --noinput

# Clear Django cache
echo "🗑️  Clearing Django cache..."
docker-compose exec appseed-app python manage.py shell -c "
from django.core.cache import cache
cache.clear()
print('Cache cleared successfully')
"

echo "✅ CSRF fix completed!"
echo ""
echo "🌐 Test your application:"
echo "   - HTTPS: https://exmanager.flimboo.com"
echo "   - Admin: https://exmanager.flimboo.com/admin"
echo ""
echo "📱 On iPhone/Android:"
echo "   - Clear browser cache and cookies"
echo "   - Try accessing the site again"
echo ""
echo "🔍 If still having issues, check logs:"
echo "   docker-compose logs -f appseed-app" 