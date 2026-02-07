/**
 * Test API route to verify Next.js API routes are working
 */
export default async function handler(req, res) {
  res.status(200).json({ 
    message: 'API route is working!',
    timestamp: new Date().toISOString(),
    method: req.method,
    headers: {
      host: req.headers.host,
    }
  })
}
