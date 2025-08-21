import type { RequestHandler } from './$types';
import { exec } from 'child_process';
import util from 'util';

const execAsync = util.promisify(exec);

export const POST: RequestHandler = async ({ request }) => {
  try {
    // Forward the request to the FastAPI endpoint
    const body = await request.json().catch(() => ({}));


    const res = await fetch("http://localhost:8000/pipeline/start", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    });

    const data = await res.json();

    return new Response(JSON.stringify(data), {
      status: res.status,
      headers: { "Content-Type": "application/json" }
    });
    
  } catch (err: any) {
    return new Response(
      JSON.stringify({
        status: 'error',
        message: err.message,
      }),
      { status: 500, headers: { 'Content-Type': 'application/json' } }
    );
  }
};
