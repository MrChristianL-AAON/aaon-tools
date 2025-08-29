import type { RequestHandler } from './$types';

export const POST: RequestHandler = async () => {
  try {
    const res = await fetch("http://localhost:8000/builder/build", {
      method: "GET",
      headers: { "Content-Type": "application/json" }
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
