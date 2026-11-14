// Cloudflare Worker that fetches euro-millions.com results pages on behalf of the
// GitHub Action, whose runner IPs are blocked by the site.
// Only /results-history-<year> is allowed, and callers must send the shared token.
//
// GET https://<worker>/?year=2026   header: X-Proxy-Token: <PROXY_TOKEN>

const UPSTREAM = "https://www.euro-millions.com/results-history-";

export default {
  async fetch(request, env) {
    if (request.method !== "GET") {
      return new Response("method not allowed", { status: 405 });
    }
    const token = request.headers.get("X-Proxy-Token") ?? "";
    if (!env.PROXY_TOKEN || !timingSafeEqual(token, env.PROXY_TOKEN)) {
      return new Response("unauthorized", { status: 401 });
    }
    const year = new URL(request.url).searchParams.get("year") ?? "";
    if (!/^20\d{2}$/.test(year)) {
      return new Response("bad year", { status: 400 });
    }

    const upstream = await fetch(UPSTREAM + year, {
      headers: {
        "User-Agent":
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        Accept: "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
      },
    });
    return new Response(upstream.body, {
      status: upstream.status,
      headers: { "Content-Type": "text/html; charset=utf-8" },
    });
  },
};

function timingSafeEqual(a, b) {
  if (a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return diff === 0;
}
