# Multi-Site Testing Guide

This guide explains how to test the multi-site functionality with different domains like `blog1.com` and `blog2.com`.

## Step 1: Set Up Local Domain Mapping (Windows)

1. **Open Notepad as Administrator**:
   - Right-click on Notepad → "Run as administrator"
   - This is required to edit the hosts file

2. **Open the hosts file**:
   - File → Open
   - Navigate to: `C:\Windows\System32\drivers\etc\`
   - Change file type filter to "All Files (*.*)"
   - Open `hosts` file

3. **Add domain mappings**:
   Add these lines at the end of the file:
   ```
   127.0.0.1 blog1.com
   127.0.0.1 blog2.com
   127.0.0.1 example.com
   ```

4. **Save the file** (Ctrl+S)

5. **Flush DNS cache** (optional but recommended):
   - Open Command Prompt as Administrator
   - Run: `ipconfig /flushdns`

## Step 2: Set Up Django Sites

Run the Django management command to create/update the sites:

```bash
cd backend
python manage.py setup_sites
```

This will create:
- Site 1: `blog1.com` (ID: 1)
- Site 2: `blog2.com` (ID: 2)

## Step 3: Create Articles for Different Sites

1. **Access Django Admin**:
   - Go to: `http://localhost:8000/admin/`
   - Login with your admin credentials

2. **Create Articles**:
   - Navigate to "Articles" → "Add Article"
   - Fill in:
     - **Title**: e.g., "Welcome to Blog 1"
     - **Content**: Your article content
     - **Published**: ✅ Check this box
     - **Sites**: Select "Blog 1" (blog1.com)
   - Save

3. **Create Articles for Blog 2**:
   - Create another article
   - This time, select "Blog 2" (blog2.com) in the Sites field

## Step 4: Test Different Domains

### Test Blog 1:
1. Open your browser
2. Go to: `http://blog1.com:3000`
3. You should see:
   - Site name: "Blog 1"
   - Domain: "blog1.com"
   - Only articles assigned to blog1.com

### Test Blog 2:
1. Open your browser (or a new tab)
2. Go to: `http://blog2.com:3000`
3. You should see:
   - Site name: "Blog 2"
   - Domain: "blog2.com"
   - Only articles assigned to blog2.com

### Test Example.com:
1. Go to: `http://example.com:3000`
2. This will use the default site (usually Site 1)

## How It Works

1. **Browser Request**: When you visit `http://blog1.com:3000`, the browser sends a request with `Host: blog1.com:3000`

2. **Next.js API Route**: The API route at `/api/articles/current_site` receives the request and extracts the Host header

3. **Proxy to Django**: The API route forwards the request to Django with `X-Forwarded-Host: blog1.com:3000` header

4. **Django Site Detection**: Django's `get_current_site()` function:
   - Reads the `X-Forwarded-Host` header (because `USE_X_FORWARDED_HOST = True`)
   - Looks up the Site object with domain matching `blog1.com`
   - Returns the matching site

5. **Content Filtering**: Django filters articles to only show those assigned to the detected site

## Troubleshooting

### Sites not detected correctly:
- Check Django admin: `http://localhost:8000/admin/sites/site/`
- Verify site domains match exactly (including port if needed)
- Check Next.js terminal for the `X-Forwarded-Host` header value

### Articles not showing:
- Verify articles are marked as `published=True`
- Check articles are assigned to the correct site(s)
- Use `/api/articles/current_site` endpoint to see which site is detected

### CORS errors:
- Make sure the domain is in `CORS_ALLOWED_ORIGINS` in `settings.py`
- Include the port number: `http://blog1.com:3000`

### Hosts file not working:
- Make sure you saved the file as Administrator
- Try flushing DNS: `ipconfig /flushdns`
- Restart your browser
- Check the hosts file doesn't have syntax errors

## Testing API Directly

You can also test the API directly using curl (or PowerShell):

```powershell
# Test blog1.com
Invoke-WebRequest -Uri "http://localhost:8000/api/articles/current_site/" -Headers @{"X-Forwarded-Host"="blog1.com:3000"}

# Test blog2.com  
Invoke-WebRequest -Uri "http://localhost:8000/api/articles/current_site/" -Headers @{"X-Forwarded-Host"="blog2.com:3000"}
```

## Next Steps

Once you've verified multi-site functionality works:
1. Create more articles for different sites
2. Test that articles only show on their assigned sites
3. Try assigning an article to multiple sites (it should appear on both)
