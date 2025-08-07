#!/bin/bash

# SSL Certificate Setup Script for exmanager.flimboo.com
# This script sets up SSL certificates for the Django application

set -e

DOMAIN="exmanager.flimboo.com"
SSL_DIR="./nginx/ssl"

echo "🔐 Setting up SSL certificates for $DOMAIN..."

# Create SSL directory
mkdir -p $SSL_DIR

# Check if we want to use Let's Encrypt or self-signed certificates
echo "Choose SSL certificate type:"
echo "1) Let's Encrypt (Recommended for production)"
echo "2) Self-signed certificate (For development/testing)"
read -p "Enter your choice (1 or 2): " choice

case $choice in
    1)
        echo "🔒 Setting up Let's Encrypt certificate..."
        
        # Check if certbot is installed
        if ! command -v certbot &> /dev/null; then
            echo "❌ Certbot is not installed. Installing..."
            sudo apt update
            sudo apt install certbot python3-certbot-nginx -y
        fi
        
        # Stop nginx temporarily
        docker-compose stop nginx
        
        # Get certificate from Let's Encrypt
        sudo certbot certonly --standalone -d $DOMAIN --email admin@flimboo.com --agree-tos --non-interactive
        
        # Copy certificates to nginx ssl directory
        sudo cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem $SSL_DIR/cert.pem
        sudo cp /etc/letsencrypt/live/$DOMAIN/privkey.pem $SSL_DIR/key.pem
        
        # Set proper permissions
        sudo chown $USER:$USER $SSL_DIR/cert.pem $SSL_DIR/key.pem
        chmod 644 $SSL_DIR/cert.pem
        chmod 600 $SSL_DIR/key.pem
        
        echo "✅ Let's Encrypt certificate installed successfully!"
        echo "📅 Certificate will auto-renew. Set up a cron job for renewal:"
        echo "   sudo crontab -e"
        echo "   Add: 0 12 * * * /usr/bin/certbot renew --quiet"
        
        ;;
    2)
        echo "🔒 Generating self-signed certificate..."
        
        # Generate self-signed certificate
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout $SSL_DIR/key.pem \
            -out $SSL_DIR/cert.pem \
            -subj "/C=EC/ST=Ecuador/L=Quito/O=Flimboo/OU=IT/CN=$DOMAIN"
        
        echo "✅ Self-signed certificate generated successfully!"
        echo "⚠️  Note: Self-signed certificates will show security warnings in browsers."
        ;;
    *)
        echo "❌ Invalid choice. Exiting."
        exit 1
        ;;
esac

echo ""
echo "🔧 SSL certificates are ready!"
echo "📁 Certificates location: $SSL_DIR/"
echo ""
echo "🚀 You can now start the application with:"
echo "   docker-compose up --build -d"
echo ""
echo "🌐 Access your application at: https://$DOMAIN" 