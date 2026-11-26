export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === "/" || url.pathname === "") {
      return env.ASSETS.fetch(new Request(new URL("/dist/index.html", request.url), request));
    }
    // Try static asset under dist/
    const assetReq = new Request(new URL("/dist" + url.pathname, request.url), request);
    const assetRes = await env.ASSETS.fetch(assetReq);
    if (assetRes.status !== 404) {
      return assetRes;
    }
    // SPA fallback: return dist/index.html
    return env.ASSETS.fetch(new Request(new URL("/dist/index.html", request.url), request));
  }
};
