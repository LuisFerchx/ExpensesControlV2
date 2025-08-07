# Docker Deployment Guide for Django AdminLTE

This guide explains how to deploy the Django AdminLTE application on Ubuntu using Docker with SSL support for `exmanager.flimboo.com`.

## 🚀 Quick Start

### Prerequisites

1. **Ubuntu Server** (18.04 or later)
2. **Docker** and **Docker Compose** installed
3. **Git** for cloning the repository
4. **Domain DNS** pointing to your server IP

### Installation Steps

1. **Install Docker and Docker Compose** (if not already installed):
   ```bash
   sudo apt update
   sudo apt install docker.io docker-compose git
   sudo usermod -aG docker $USER
   # Log out and log back in for group changes to take effect
   ```

2. **Clone the repository**:
   ```bash
   git clone <your-repository-url>
   cd django-adminlte
   ```

3. **Run the deployment script**:
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

## 🔐 SSL Configuration

The application is configured to run with HTTPS on `exmanager.flimboo.com`.

### SSL Certificate Options

1. **Let's Encrypt (Recommended for production)**:
   ```bash
   chmod +x ssl-setup.sh
   ./ssl-setup.sh
   # Choose option 1 for Let's Encrypt
   ```

2. **Self-signed certificate (For development/testing)**:
   ```bash
   chmod +x ssl-setup.sh
   ./ssl-setup.sh
   # Choose option 2 for self-signed
   ```

### SSL Certificate Renewal

For Let's Encrypt certificates, set up automatic renewal:

```bash
# Add to crontab for automatic renewal
sudo crontab -e
# Add this line:
0 12 * * * /path/to/your/django-adminlte/ssl-renew.sh
```

Or manually renew:
```bash
chmod +x ssl-renew.sh
./ssl-renew.sh
```

## 📋 Manual Deployment

If you prefer to deploy manually:

### 1. Environment Configuration

Create a `.env` file based on the template:
```bash
cp env.production .env
```

Edit `.env` with your production settings:
```bash
nano .env
```

**Important settings to configure:**
- `SECRET_KEY`: Generate a strong secret key
- `DEBUG`: Set to `False` for production
- `ALLOWED_HOSTS`: Should include `exmanager.flimboo.com`
- `CSRF_TRUSTED_ORIGINS`: Should include `https://exmanager.flimboo.com`

### 2. SSL Certificate Setup

```bash
# Create SSL directory
mkdir -p nginx/ssl

# Set up SSL certificates
chmod +x ssl-setup.sh
./ssl-setup.sh
```

### 3. Build and Start Containers

```bash
# Build and start all services
docker-compose up --build -d

# Check container status
docker-compose ps
```

### 4. Database Setup

```bash
# Run migrations
docker-compose exec appseed-app python manage.py migrate

# Create superuser (optional)
docker-compose exec appseed-app python manage.py createsuperuser

# Collect static files
docker-compose exec appseed-app python manage.py collectstatic --noinput
```

## 🏗️ Architecture

The application uses the following Docker services:

- **appseed-app**: Django application (Python 3.9)
- **db**: PostgreSQL 15 database
- **nginx**: Web server and reverse proxy with SSL

### Ports

- **80**: HTTP (redirects to HTTPS)
- **443**: HTTPS (main application)
- **5432**: PostgreSQL (database)

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Django debug mode | `False` |
| `SECRET_KEY` | Django secret key | Required |
| `DB_ENGINE` | Database engine | `postgresql` |
| `DB_HOST` | Database host | `db` |
| `DB_NAME` | Database name | `django_db` |
| `DB_USERNAME` | Database user | `django_user` |
| `DB_PASS` | Database password | `django_password` |
| `DB_PORT` | Database port | `5432` |
| `ALLOWED_HOSTS` | Django allowed hosts | `exmanager.flimboo.com,localhost,127.0.0.1` |
| `CSRF_TRUSTED_ORIGINS` | CSRF trusted origins | `https://exmanager.flimboo.com,http://localhost,http://127.0.0.1` |

### Volumes

- `postgres_data`: PostgreSQL data persistence
- `static_volume`: Static files
- `media_volume`: Media files

## 🛠️ Management Commands

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f appseed-app
```

### Stop Services
```bash
docker-compose down
```

### Restart Services
```bash
docker-compose restart
```

### Update Application
```bash
git pull
docker-compose up --build -d
```

### SSL Certificate Management
```bash
# Set up SSL certificates
./ssl-setup.sh

# Renew SSL certificates
./ssl-renew.sh

# Check certificate expiration
openssl x509 -in nginx/ssl/cert.pem -text -noout | grep -A 2 "Validity"
```

### Database Backup
```bash
docker-compose exec appseed-app python manage.py dbbackup
```

### Database Restore
```bash
docker-compose exec appseed-app python manage.py dbrestore
```

## 🔒 Security Considerations

1. **Change default passwords** in `.env`
2. **Use strong SECRET_KEY**
3. **SSL/TLS is configured** for production
4. **Set up firewall** rules
5. **Regular backups** of database and media files
6. **SSL certificate renewal** is automated

## 📊 Monitoring

### Health Checks

The application includes health checks:
- Database: `pg_isready`
- Application: `curl -f http://localhost:5005/`
- SSL: Certificate expiration monitoring

### Logs

Monitor application logs:
```bash
docker-compose logs -f appseed-app
```

## 🚨 Troubleshooting

### Common Issues

1. **SSL certificate issues**:
   ```bash
   # Check certificate validity
   openssl x509 -in nginx/ssl/cert.pem -text -noout
   
   # Renew certificates
   ./ssl-renew.sh
   ```

2. **Port already in use**:
   ```bash
   sudo netstat -tulpn | grep :80
   sudo netstat -tulpn | grep :443
   sudo systemctl stop apache2  # if Apache is running
   ```

3. **Permission issues**:
   ```bash
   sudo chown -R $USER:$USER .
   chmod 600 nginx/ssl/key.pem
   chmod 644 nginx/ssl/cert.pem
   ```

4. **Database connection issues**:
   ```bash
   docker-compose logs db
   docker-compose restart db
   ```

5. **Static files not loading**:
   ```bash
   docker-compose exec appseed-app python manage.py collectstatic --noinput
   ```

### Debug Mode

For development, use the development compose file:
```bash
docker-compose -f docker-compose.dev.yml up --build
```

## 📝 Development

For local development:

1. Use `docker-compose.dev.yml`:
   ```bash
   docker-compose -f docker-compose.dev.yml up --build
   ```

2. Access the application at `http://localhost:8000`

3. The development setup uses SQLite and DEBUG=True

## 🔄 Updates

To update the application:

1. Pull latest changes:
   ```bash
   git pull origin main
   ```

2. Rebuild and restart:
   ```bash
   docker-compose up --build -d
   ```

3. Run migrations if needed:
   ```bash
   docker-compose exec appseed-app python manage.py migrate
   ```

4. Renew SSL certificates if needed:
   ```bash
   ./ssl-renew.sh
   ```

## 🌐 Domain Configuration

### DNS Setup

Ensure your domain `exmanager.flimboo.com` points to your server's IP address:

```bash
# Check if domain resolves correctly
nslookup exmanager.flimboo.com
dig exmanager.flimboo.com
```

### Firewall Configuration

```bash
# Allow HTTP and HTTPS traffic
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable
```

## 📞 Support

For issues or questions:
1. Check the logs: `docker-compose logs`
2. Verify environment variables
3. Ensure all ports are available
4. Check Docker and Docker Compose versions
5. Verify SSL certificate validity
6. Check domain DNS configuration 