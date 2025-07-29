# Docker Deployment Guide for Django AdminLTE

This guide explains how to deploy the Django AdminLTE application on Ubuntu using Docker.

## 🚀 Quick Start

### Prerequisites

1. **Ubuntu Server** (18.04 or later)
2. **Docker** and **Docker Compose** installed
3. **Git** for cloning the repository

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
- `ALLOWED_HOSTS`: Add your domain
- `CSRF_TRUSTED_ORIGINS`: Add your domain with https://

### 2. Build and Start Containers

```bash
# Build and start all services
docker-compose up --build -d

# Check container status
docker-compose ps
```

### 3. Database Setup

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
- **nginx**: Web server and reverse proxy

### Ports

- **80**: HTTP (nginx)
- **443**: HTTPS (nginx, if configured)
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
3. **Configure SSL/TLS** for production
4. **Set up firewall** rules
5. **Regular backups** of database and media files

## 📊 Monitoring

### Health Checks

The application includes health checks:
- Database: `pg_isready`
- Application: `curl -f http://localhost:5005/`

### Logs

Monitor application logs:
```bash
docker-compose logs -f appseed-app
```

## 🚨 Troubleshooting

### Common Issues

1. **Port already in use**:
   ```bash
   sudo netstat -tulpn | grep :80
   sudo systemctl stop apache2  # if Apache is running
   ```

2. **Permission issues**:
   ```bash
   sudo chown -R $USER:$USER .
   ```

3. **Database connection issues**:
   ```bash
   docker-compose logs db
   docker-compose restart db
   ```

4. **Static files not loading**:
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

## 📞 Support

For issues or questions:
1. Check the logs: `docker-compose logs`
2. Verify environment variables
3. Ensure all ports are available
4. Check Docker and Docker Compose versions 