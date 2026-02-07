import { useState, useEffect } from 'react'
import Head from 'next/head'

/**
 * Homepage component that fetches and displays articles from the Django backend.
 * 
 * The component automatically detects the current domain using window.location.host
 * and makes API requests that include the correct Host header. The Django backend
 * uses this Host header to determine which site's content to return.
 * 
 * This means:
 * - When accessed via blog1.com, it shows articles for blog1.com
 * - When accessed via blog2.com, it shows articles for blog2.com
 * - No manual site ID passing is required
 */
export default function Home() {
  const [articles, setArticles] = useState([])
  const [siteInfo, setSiteInfo] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    /**
     * Get the API base URL.
     * 
     * In development, Next.js rewrites (configured in next.config.js) proxy
     * /api/* requests to the Django backend, preserving the Host header.
     * 
     * In production, the API would be on the same domain or a configured API domain.
     * The browser automatically sets the Host header based on the URL.
     */
    const getApiBaseUrl = () => {
      if (typeof window === 'undefined') {
        return ''
      }
      
      // Use relative URLs - Next.js rewrites will proxy to Django backend
      // This preserves the Host header (e.g., blog1.com) so Django can detect the site
      // Note: Make sure Next.js dev server is running and next.config.js rewrites are configured
      return ''
    }

    /**
     * Fetch articles from the Django backend.
     * 
     * The backend automatically detects the site from the Host header
     * in the request. The browser sets the Host header automatically based
     * on the URL being requested - we cannot manually set it for security reasons.
     * 
     * For this to work correctly:
     * - In production: Frontend and backend should be on the same domain
     * - In development: Use /etc/hosts to map blog1.com/blog2.com to 127.0.0.1
     */
    const fetchArticles = async () => {
      try {
        setLoading(true)
        const apiBaseUrl = getApiBaseUrl()
        
        // First, test if API routes are working at all
        try {
          const testResponse = await fetch('/api/simple-test')
          const testData = await testResponse.json()
          console.log('API route test successful:', testData)
        } catch (testErr) {
          console.error('API route test failed:', testErr)
          throw new Error(`API routes not working: ${testErr.message}. Make sure Next.js dev server is running and API routes are accessible.`)
        }
        
        // Fetch current site information
        // Next.js API route proxies this to Django backend, preserving Host header
        console.log('Fetching from /api/articles/current_site')
        
        // First test if the route path works
        try {
          const testRouteResponse = await fetch('/api/articles/current_site-test')
          const testRouteData = await testRouteResponse.json()
          console.log('Route path test successful:', testRouteData)
        } catch (testErr) {
          console.error('Route path test failed:', testErr)
        }
        
        // Fetch without trailing slash to avoid redirect issues
        // Add cache-busting to avoid cached redirects
        const siteResponse = await fetch('/api/articles/current_site?t=' + Date.now(), {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
          cache: 'no-store', // Don't cache to avoid redirect issues
        })
        
        console.log('Site response status:', siteResponse.status, siteResponse.statusText)
        
        if (!siteResponse.ok) {
          const errorText = await siteResponse.text().catch(() => 'Unknown error')
          console.error('Site response error:', errorText)
          throw new Error(`Failed to fetch site information: ${siteResponse.status} ${errorText}`)
        }
        
        const siteData = await siteResponse.json()
        setSiteInfo(siteData)
        
        // Fetch articles - the backend filters by current site automatically
        // The Host header (preserved by Next.js rewrite) tells Django which site to use
        const articlesResponse = await fetch('/api/articles/', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        })
        
        if (!articlesResponse.ok) {
          const errorText = await articlesResponse.text().catch(() => 'Unknown error')
          throw new Error(`Failed to fetch articles: ${articlesResponse.status} ${errorText}`)
        }
        
        const articlesData = await articlesResponse.json()
        setArticles(articlesData.results || articlesData)
        setError(null)
      } catch (err) {
        console.error('Error fetching articles:', err)
        // Provide more helpful error messages
        if (err.message.includes('Failed to fetch') || err.name === 'TypeError') {
          setError('Cannot connect to the backend. Make sure: 1) Django server is running on http://localhost:8000, 2) Next.js API routes are working (check /api/test), 3) Check browser console and Next.js terminal for detailed errors')
        } else {
          setError(err.message)
        }
      } finally {
        setLoading(false)
      }
    }

    fetchArticles()
  }, [])

  return (
    <>
      <Head>
        <title>Multi-Site Blog</title>
        <meta name="description" content="Multi-site blog powered by Django Sites framework" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className="container">
        <header className="header">
          <h1 className="title">
            {siteInfo ? siteInfo.name : 'Multi-Site Blog'}
          </h1>
          {siteInfo && (
            <p className="subtitle">
              Domain: {siteInfo.domain}
            </p>
          )}
        </header>

        {loading && (
          <div className="loading">
            <p>Loading articles...</p>
          </div>
        )}

        {error && (
          <div className="error">
            <p>Error: {error}</p>
            <p className="error-hint">
              Make sure the Django backend is running on http://localhost:8000
            </p>
          </div>
        )}

        {!loading && !error && (
          <>
            {articles.length === 0 ? (
              <div className="empty-state">
                <p>No articles found for this site.</p>
                <p className="hint">
                  Create articles in the Django admin and assign them to this site.
                </p>
              </div>
            ) : (
              <div className="articles">
                <h2 className="articles-title">Articles ({articles.length})</h2>
                {articles.map((article) => (
                  <article key={article.id} className="article-card">
                    <h3 className="article-title">{article.title}</h3>
                    <p className="article-date">
                      {new Date(article.created_at).toLocaleDateString('en-US', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric'
                      })}
                    </p>
                    <div className="article-content">
                      {article.content.split('\n').map((paragraph, index) => (
                        <p key={index}>{paragraph}</p>
                      ))}
                    </div>
                  </article>
                ))}
              </div>
            )}
          </>
        )}
      </main>
    </>
  )
}
