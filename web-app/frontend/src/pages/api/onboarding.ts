import type { APIRoute } from "astro";

export const prerender = false;

export const POST: APIRoute = async ({ cookies }) => {
	cookies.set("onboarded", "true", {
		path: "/",
		maxAge: 60 * 60 * 24 * 365, // 1 year
		httpOnly: true,
		secure: true,
		sameSite: "lax",
	});

	return new Response(JSON.stringify({ ok: true }), { status: 200 });
};
