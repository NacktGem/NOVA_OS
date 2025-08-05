import type { NextApiRequest, NextApiResponse } from 'next';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') return res.status(405).end();
  const { theme } = req.body;
  await fetch(`${process.env.BACKEND_URL || 'http://localhost:8000'}/payment/charge`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ theme })
  });
  res.status(200).json({ purchased: theme });
}
