# Multi-Site Blog System

A production-ready multi-site blog system using Django + Django REST Framework for the backend and Next.js for the frontend. A single Django backend serves multiple blog websites (domains) using the Django Sites framework.

## Overview

This system allows you to:
- Serve multiple blog domains from a single Django backend
- Publish articles to one site only (e.g., blog1.com)
- Publish articles to multiple sites (e.g., both blog1.com and blog2.com)
- Automatically filter content based on the current domain
- Use the same API endpoints for all domains without code changes

## Architecture

### Backend (Django + DRF)
- Uses Django's Sites framework to manage multiple domains
- Article model with ManyToManyField to Site
- REST API that automatically detects the current site from the request's Host header
- No hardcoded domains - site detection is dynamic

### Frontend (Next.js)
- Automatically detects the current domain using `window.location.host`
- Makes API requests that include the correct Host header
- Displays site-specific content without manual configuration

## Why Django Sites Framework?

The Django Sites framework is essential for this multi-site architecture because:

1. **Domain Detection**: It allows Django to identify which site (domain) is making a request based on the HTTP Host header
2. **Content Filtering**: Articles can be associated with one or multiple sites, enabling flexible content distribution
3. **Single Codebase**: One Django instance can serve multiple domains without code duplication
4. **Automatic Routing**: The same API endpoints work for all domains - the framework handles the routing automatically

## How Content is Filtered Per Domain

1. **Request Arrives**: When a request comes to `/api/articles/`, Django receives the HTTP Host header (e.g., `blog1.com` or `blog2.com`)

2. **Site Detection**: The API view uses `get_current_site(request)` which:
   - Reads the Host header from the request
   - Looks up the corresponding Site object in the database
   - Returns the current site

3. **Content Filtering**: The queryset filters articles by:
   - `published=True` (only published articles)
   - `sites=current_site` (only articles linked to the current site)

4. **Response**: Only articles assigned to the current site are returned

This means:
- `blog1.com/api/articles/` → Returns only articles for blog1.com
- `blog2.com/api/articles/` → Returns only articles for blog2.com
- The same code works for both domains

## Project Structure

```
.
├── backend/
│   ├── blog/                    # Blog application
│   │   ├── models.py            # Article model with Sites ManyToMany
│   │   ├── admin.py             # Admin with required site selection
│   │   ├── views.py             # API views with site detection
│   │   ├── serializers.py       # DRF serializers
│   │   └── urls.py              # API URL routing
│   ├── blogproject/             # Django project settings
│   │   ├── settings.py          # Sites framework configuration
│   │   └── urls.py              # Main URL configuration
│   ├── manage.py
│   └── requirements.txt
├── frontend/
│   ├── pages/
│   │   ├── index.js             # Homepage with article fetching
│   │   └── _app.js              # Next.js app wrapper
│   ├── styles/
│   │   └── globals.css          # Global styles
│   └── package.json
└── README.md
```

## Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js 18+
- npm or yarn

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

5. **Create initial sites**:
   ```bash
   python manage.py shell
   ```
   
   Then in the shell:
   ```python
   from django.contrib.sites.models import Site
   
   # Create or update Site 1
   site1, created = Site.objects.get_or_create(
       id=1,
       defaults={'domain': 'blog1.com', 'name': 'Blog 1'}
   )
   if not created:
       site1.domain = 'blog1.com'
       site1.name = 'Blog 1'
       site1.save()
   
   # Create or update Site 2
   site2, created = Site.objects.get_or_create(
       id=2,
       defaults={'domain': 'blog2.com', 'name': 'Blog 2'}
   )
   if not created:
       site2.domain = 'blog2.com'
       site2.name = 'Blog 2'
       site2.save()
   
   print(f"Site 1: {site1.domain} (ID: {site1.id})")
   print(f"Site 2: {site2.domain} (ID: {site2.id})")
   ```

6. **Create superuser** (for admin access):
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server**:
   ```bash
   python manage.py runserver
   ```

   The backend will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Run development server**:
   ```bash
   npm run dev
   ```

   The frontend will be available at `http://localhost:3000`

## Usage

### Creating Articles

1. Access Django admin at `http://localhost:8000/admin`
2. Log in with your superuser credentials
3. Navigate to "Articles" → "Add Article"
4. Fill in:
   - Title
   - Content
   - Published (check to publish)
   - Sites (select one or more sites - **required**)
5. Save the article

### Testing Multi-Site Functionality

#### Option 1: Using /etc/hosts (Recommended for Development)

The frontend uses Next.js rewrites to proxy API requests to the Django backend, preserving the Host header. To test different sites:

1. **Modify your hosts file**:
   - Linux/Mac: `/etc/hosts`
   - Windows: `C:\Windows\System32\drivers\etc\hosts`
   
   Add these lines:
   ```
   127.0.0.1 blog1.com
   127.0.0.1 blog2.com
   ```

2. **Access the frontend via the mapped domains**:
   - `http://blog1.com:3000` → Shows articles for blog1.com
   - `http://blog2.com:3000` → Shows articles for blog2.com

3. **How it works**:
   - Browser makes request to `blog1.com:3000/api/articles/`
   - Next.js rewrite proxies to `http://localhost:8000/api/articles/`
   - The original Host header (`blog1.com`) is preserved
   - Django detects `blog1.com` from the Host header and returns matching articles

#### Option 2: Direct API Testing with curl

You can test the API directly by setting the Host header:

```bash
# Test blog1.com
curl -H "Host: blog1.com" http://localhost:8000/api/articles/

# Test blog2.com
curl -H "Host: blog2.com" http://localhost:8000/api/articles/

# Get current site info
curl -H "Host: blog1.com" http://localhost:8000/api/articles/current_site/
```

### API Endpoints

- `GET /api/articles/` - List all published articles for the current site
- `GET /api/articles/{id}/` - Get a specific article
- `GET /api/articles/current_site/` - Get information about the current site

All endpoints automatically filter by the current site based on the Host header.

## Key Implementation Details

### Backend Site Detection

In `backend/blog/views.py`:
```python
from django.contrib.sites.shortcuts import get_current_site

def get_queryset(self):
    current_site = get_current_site(self.request)
    return Article.objects.filter(
        published=True,
        sites=current_site
    ).distinct()
```

### Frontend Domain Handling

The frontend uses Next.js rewrites (configured in `next.config.js`) to proxy API requests:

```javascript
// next.config.js
async rewrites() {
  return [
    {
      source: '/api/:path*',
      destination: 'http://localhost:8000/api/:path*',
    },
  ]
}
```

This preserves the original Host header when proxying, so:
- Request to `blog1.com:3000/api/articles/` → Proxied to Django with Host: `blog1.com`
- Request to `blog2.com:3000/api/articles/` → Proxied to Django with Host: `blog2.com`

The frontend code in `pages/index.js` uses relative URLs (`/api/articles/`), which work with the rewrite proxy.

### SITE_ID in Settings

The `SITE_ID = 1` setting in `settings.py` is used as:
- A default/fallback when Sites framework needs a site
- For Django admin initialization
- For management commands without request context

**Important**: The actual site detection in API views uses `get_current_site(request)`, which reads from the request's Host header, not from `SITE_ID`.

## Production Considerations

1. **Domain Configuration**: Update `ALLOWED_HOSTS` in `settings.py` with your production domains
2. **CORS Settings**: Update `CORS_ALLOWED_ORIGINS` with your frontend domains
3. **Database**: Use PostgreSQL or MySQL instead of SQLite for production
4. **Static Files**: Configure proper static file serving (e.g., WhiteNoise, S3, CDN)
5. **Security**: Change `SECRET_KEY`, disable `DEBUG`, and configure proper security headers
6. **Site Objects**: Ensure Site objects in the database match your production domains

## Troubleshooting

### Articles not showing up
- Check that articles are marked as `published=True`
- Verify articles are assigned to the correct site(s)
- Ensure the Host header matches a Site domain in the database

### CORS errors
- Update `CORS_ALLOWED_ORIGINS` in `settings.py` with your frontend URL
- Ensure the frontend is making requests to the correct backend URL

### Site detection not working
- Verify Site objects exist in the database with correct domains
- Check that the Host header in requests matches a Site domain
- Use the `/api/articles/current_site/` endpoint to debug site detection

## License

This project is provided as-is for educational and development purposes.
