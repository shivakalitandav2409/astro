export default {
  async fetch(request, env) {
    // Try serving the asset directly (ASSETS binding roots at dist/)
    try {
      const res = await env.ASSETS.fetch(request);
      if (res.status !== 404) return res;
    } catch {}
    // SPA fallback: always serve index.html for client-side routing
    return env.ASSETS.fetch(
      new Request(new URL("/index.html", request.url), request)
    );
  }
};
