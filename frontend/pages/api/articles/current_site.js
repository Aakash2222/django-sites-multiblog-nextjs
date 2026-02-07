/**
 * Next.js API route that proxies requests to Django backend for current_site endpoint.
 * 
 * This preserves the Host header from the original request so Django can
 * detect which site the request is for (multi-site functionality).
 */
export default async function handler(req, res) {
  // Log that the API route was hit
  console.log('API route hit: /api/articles/current_site', {
    method: req.method,
    host: req.headers.host,
    url: req.url
  })

  // Set timeout to prevent hanging
  const timeout = setTimeout(() => {
    if (!res.headersSent) {
      res.status(504).json({ error: 'Request timeout' })
    }
  }, 10000) // 10 second timeout

  try {
    if (req.method !== 'GET') {
      clearTimeout(timeout)
      return res.status(405).json({ error: 'Method not allowed' })
    }
    // Get the original Host header from the request
    // This is crucial for Django's Sites framework to detect the correct site
    const originalHost = req.headers.host || req.headers['x-forwarded-host'] || 'localhost:3000'
    
    // Strip port number from host for Django site matching
    // Django sites are configured as "blog1.com" not "blog1.com:3000"
    const hostWithoutPort = originalHost.split(':')[0]
    
    // Construct the Django backend URL
    const backendUrl = 'http://localhost:8000/api/articles/current_site/'
    
    console.log('Proxying to Django:', {
      backendUrl,
      originalHost,
      hostWithoutPort,
      headers: {
        'X-Forwarded-Host': hostWithoutPort, // Pass host without port for site detection
        'X-Forwarded-Proto': req.headers['x-forwarded-proto'] || 'http',
      }
    })
    
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
    
    console.log('Django response status:', response.status)
    
    if (!response.ok) {
      const errorText = await response.text().catch(() => 'Unknown error')
      console.error('Django returned error:', response.status, errorText)
      return res.status(response.status).json({ 
        error: 'Failed to fetch from Django backend',
        status: response.status,
        details: errorText 
      })
    }
    
    const data = await response.json()
    console.log('Django returned site data:', data)
    console.log('Successfully proxied response from Django')
    clearTimeout(timeout)
    res.status(200).json(data)
  } catch (error) {
    clearTimeout(timeout)
    console.error('Proxy error:', error)
    console.error('Error details:', {
      message: error.message,
      name: error.name,
      code: error.code,
      stack: error.stack,
      backendUrl: 'http://localhost:8000/api/articles/current_site/',
      originalHost: req.headers.host
    })
    
    // Make sure we haven't already sent a response
    if (!res.headersSent) {
      res.status(500).json({ 
        error: 'Failed to proxy request to Django backend',
        message: error.message,
        code: error.code,
        details: process.env.NODE_ENV === 'development' ? error.stack : undefined
      })
    }
  }
}
