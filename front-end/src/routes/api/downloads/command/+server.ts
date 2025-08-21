// +server.ts
import { json } from '@sveltejs/kit';

export const GET = async () => {
  // Get list of files from API
  const res = await fetch('http://localhost:8000/command');
  const data = await res.json();

  if (!data.files || data.files.length === 0) {
    return json({ error: 'No files available' }, { status: 404 });
  }

  // Example: pick latest by sorting (depends on your naming convention)
  const latestFile = data.files.sort().reverse()[0];

  // Call the download endpoint
  const fileRes = await fetch(`http://localhost:8000/command/${latestFile}`);

  // Return as stream so browser downloads
  return new Response(fileRes.body, {
    headers: {
      'Content-Disposition': `attachment; filename="${latestFile}"`,
      'Content-Type': fileRes.headers.get('content-type') || 'application/octet-stream'
    }
  });
};
