// src/routes/api/builder/output_files/+server.ts
import type { RequestHandler } from './$types';

const FASTAPI_BASE = 'http://127.0.0.1:8000/api/builder';

export const GET: RequestHandler = async () => {
  const res = await fetch(`${FASTAPI_BASE}/output_files`, {
    method: 'GET'
  });

  const data = await res.json();
  return new Response(JSON.stringify(data), {
    status: res.status,
    headers: { 'Content-Type': 'application/json' }
  });
};
