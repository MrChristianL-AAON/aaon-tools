import type { RequestHandler } from '../$types';

export const POST: RequestHandler = async ({ request }) => {
    const formData = await request.formData();
    const file = formData.get('file') as File | null;

    if (!file) {
        return new Response(
            JSON.stringify({ detail: "File is required" }),
            { status: 400, headers: { "Content-Type": "application/json" } }
        );
    }

    // Forward FormData to FastAPI
    const forwardData = new FormData();
    forwardData.append('file', file);

    const res = await fetch("http://localhost:8000/inputs/json-file", {
        method: "POST",
        body: forwardData
    });

    const data = await res.json();

    return new Response(JSON.stringify(data), {
        headers: { "Content-Type": "application/json" },
        status: res.status
    });
};
