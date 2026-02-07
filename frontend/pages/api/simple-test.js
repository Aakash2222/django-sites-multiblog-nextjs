// Simple test API route
export default function handler(req, res) {
  res.status(200).json({ working: true, message: 'API route is accessible' })
}
