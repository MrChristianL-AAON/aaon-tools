// src/routes/api/upload_debs/+server.ts
import type { RequestHandler } from './$types';

const FASTAPI_BASE = 'http://127.0.0.1:8000/api/builder/';

export const POST: RequestHandler = async ({ request }) => {
  const formData = await request.formData();

  const res = await fetch(`${FASTAPI_BASE}/build_update`, {
    method: 'POST',
    body: formData
  });

  const data = await res.json();
  return new Response(JSON.stringify(data), {
    status: res.status,
    headers: { 'Content-Type': 'application/json' }
  });
};
