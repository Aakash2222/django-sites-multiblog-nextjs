/**
 * Next.js API route that proxies requests to Django backend for articles endpoint.
 * 
 * This preserves the Host header from the original request so Django can
 * detect which site the request is for (multi-site functionality).
 */
export default async function handler(req, res) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' })
  }

  try {
    // Get the original Host header from the request
    // This is crucial for Django's Sites framework to detect the correct site
    const originalHost = req.headers.host || req.headers['x-forwarded-host'] || 'localhost:3000'
    
    // Strip port number from host for Django site matching
    // Django sites are configured as "blog1.com" not "blog1.com:3000"
    const hostWithoutPort = originalHost.split(':')[0]
    
    // Construct the Django backend URL
    const backendUrl = 'http://localhost:8000/api/articles/'
    
    // Forward the request to Django backend
    // Pass the original Host (without port) via X-Forwarded-Host header
    // Django's get_current_site() will check this header when behind a proxy
    const response = await fetch(backendUrl, {
      method: 'GET',
      headers: {
        'X-Forwarded-Host': hostWithoutPort, // Pass host without port for site detection
        'X-Forwarded-Proto': req.headers['x-forwarded-proto'] || 'http',
        'Content-Type': 'application/json',
      },
    })
    
    if (!response.ok) {
      const errorText = await response.text().catch(() => 'Unknown error')
      return res.status(response.status).json({ 
        error: 'Failed to fetch from Django backend',
        details: errorText 
      })
    }
    
    const data = await response.json()
    console.log(`Django returned ${data.results?.length || data.length || 0} articles for host: ${hostWithoutPort}`)
    res.status(200).json(data)
  } catch (error) {
    console.error('Proxy error:', error)
    res.status(500).json({ 
      error: 'Failed to proxy request to Django backend',
      message: error.message 
    })
  }
}
