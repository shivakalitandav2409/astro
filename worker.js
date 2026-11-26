export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // Try serving the asset directly (ASSETS binding roots at dist/)
    try {
      const res = await env.ASSETS.fetch(request);
      // Only return if it's a real asset (not a redirect or 404)
      if (res.status !== 404 && res.status !== 307 && res.status !== 301) {
        return res;
      }
    } catch {}

    // SPA fallback: serve index.html for all client-side routes
    const indexUrl = new URL("/index.html", url.origin);
    return env.ASSETS.fetch(new Request(indexUrl.toString(), {
      method: "GET",
      headers: request.headers,
    }));
  }
};
