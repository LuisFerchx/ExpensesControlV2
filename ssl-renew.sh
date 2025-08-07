#!/bin/bash

# SSL Certificate Renewal Script for exmanager.flimboo.com
# This script renews Let's Encrypt certificates and restarts nginx

set -e

DOMAIN="exmanager.flimboo.com"
SSL_DIR="./nginx/ssl"

echo "🔄 Renewing SSL certificates for $DOMAIN..."

# Stop nginx temporarily
echo "🛑 Stopping nginx container..."
docker-compose stop nginx

# Renew certificate
echo "🔒 Renewing Let's Encrypt certificate..."
sudo certbot renew --quiet

# Copy renewed certificates
echo "📋 Copying renewed certificates..."
sudo cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem $SSL_DIR/cert.pem
sudo cp /etc/letsencrypt/live/$DOMAIN/privkey.pem $SSL_DIR/key.pem

# Set proper permissions
sudo chown $USER:$USER $SSL_DIR/cert.pem $SSL_DIR/key.pem
chmod 644 $SSL_DIR/cert.pem
chmod 600 $SSL_DIR/key.pem

# Restart nginx
echo "🚀 Restarting nginx container..."
docker-compose up -d nginx

echo "✅ SSL certificate renewal completed successfully!"
echo "🌐 Your application is running at: https://$DOMAIN"

# Check certificate expiration
echo "📅 Certificate expiration info:"
openssl x509 -in $SSL_DIR/cert.pem -text -noout | grep -A 2 "Validity" 