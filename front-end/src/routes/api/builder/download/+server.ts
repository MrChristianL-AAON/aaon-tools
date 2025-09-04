// src/routes/api/builder/download/+server.ts
import type { RequestHandler } from './$types';

const FASTAPI_BASE = 'http://127.0.0.1:8000/api/builder';

export const GET: RequestHandler = async ({ url }) => {
  // Extract the file path from the URL
  const filePath = url.pathname.split('/api/builder/download/')[1];
  
  if (!filePath) {
    return new Response(JSON.stringify({ error: 'No file path provided' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' }
    });
  }

  try {
    const decodedPath = decodeURIComponent(filePath);
    const res = await fetch(`${FASTAPI_BASE}/download/${decodedPath}`, {
      method: 'GET'
    });

    if (!res.ok) {
      const errorText = await res.text();
      console.error('Download failed with status:', res.status, errorText);
      return new Response(JSON.stringify({ error: `Download failed: ${res.statusText}` }), {
        status: res.status,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    // Stream the file directly from the FastAPI server to the client
    const blob = await res.blob();
    return new Response(blob, {
      status: 200,
      headers: {
        'Content-Type': res.headers.get('Content-Type') || 'application/octet-stream',
        'Content-Disposition': res.headers.get('Content-Disposition') || `attachment; filename="${decodedPath.split('/').pop()}"`
      }
    });
  } catch (error) {
    console.error('Error downloading file:', error);
    return new Response(JSON.stringify({ error: 'Server error during download' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
};
