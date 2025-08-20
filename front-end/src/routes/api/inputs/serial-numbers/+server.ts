import type { RequestHandler } from '../$types';

export const POST: RequestHandler = async ({ request }) => {
    let bodyText = await request.text();

    const lines = bodyText
        .split("\n")
        .map(line => line.trim())
        .filter(line => line.length > 0);

    // Ensure exactly two lines (serial1, serial2)
    if (lines.length !== 2) {
        return new Response(
            JSON.stringify({ detail: "Two serial numbers are required" }),
            { status: 400, headers: { "Content-Type": "application/json" } }
        );
    }

    // Reassemble into JSON for FastAPI
    const payload = { serial1: lines[0], serial2: lines[1] };

    const res = await fetch("http://localhost:8000/inputs/serial-numbers", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    });

    const data = await res.json();

    return new Response(JSON.stringify(data), {
        headers: { "Content-Type": "application/json" },
        status: res.status
    });
};