/**
 * Test version of current_site route - returns immediately without calling Django
 */
export default async function handler(req, res) {
  console.log('TEST route hit: /api/articles/current_site-test')
  
  // Return immediately without calling Django
  res.status(200).json({ 
    test: true,
    message: 'API route is working - this is a test response',
    host: req.headers.host
  })
}
