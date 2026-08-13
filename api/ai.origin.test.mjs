/* Extracts sameOrigin() from api/ai.js and exercises the header combinations
   that matter: real browsers must pass, scripted callers must not. */
import { readFileSync } from "node:fs";
const src = readFileSync("api/ai.js", "utf8");
const m = src.match(/function sameOrigin\(req\)\s*\{[\s\S]*?\n\}/);
if (!m) { console.log("could not extract sameOrigin"); process.exit(1); }
const sameOrigin = new Function("req", m[0] + "\nreturn sameOrigin(req);");

const HOST = "the-sporve-web.vercel.app";
const cases = [
  // [label, headers, expected, why]
  ["Chrome/Firefox same-origin (measured)", {host:HOST, origin:`https://${HOST}`, referer:`https://${HOST}/`, "sec-fetch-site":"same-origin"}, true, "the app's real request"],
  ["Safari style: Referer only",            {host:HOST, referer:`https://${HOST}/`}, true, "older Safari omits Origin on same-origin POST"],
  ["Origin only, no Referer",               {host:HOST, origin:`https://${HOST}`}, true, "strict referrer policy"],
  ["Sec-Fetch-Site only",                   {host:HOST, "sec-fetch-site":"same-origin"}, true, "privacy setup stripping Origin+Referer"],
  ["preview deployment host",               {host:"sporve-git-abc.vercel.app", origin:"https://sporve-git-abc.vercel.app", "sec-fetch-site":"same-origin"}, true, "per-branch hostnames must work"],
  ["cross-site browser request",            {host:HOST, origin:"https://evil.example.com", "sec-fetch-site":"cross-site"}, false, "the attack a browser can mount"],
  ["foreign Origin, no Sec-Fetch",          {host:HOST, origin:"https://evil.example.com"}, false, "older browser, foreign page"],
  ["BARE CURL - no headers at all",         {host:HOST}, false, "THE FIX: was allowed, now rejected"],
  ["curl with only content-type",           {host:HOST, "content-type":"application/json"}, false, "scripted abuse path"],
  ["malformed Origin",                      {host:HOST, origin:"not a url"}, false, "garbage in"],
  ["no host header",                        {origin:`https://${HOST}`}, false, "cannot verify anything"],
  ["cross-site via x-forwarded-host",        {"x-forwarded-host":HOST, host:"internal", origin:"https://evil.example.com","sec-fetch-site":"cross-site"}, false, "proxy header respected"],
];
let pass=0, fail=0;
for (const [label, headers, expected, why] of cases) {
  const got = sameOrigin({ headers });
  const ok = got === expected;
  ok ? pass++ : fail++;
  console.log(`  ${ok?"PASS":"FAIL"}  ${label.padEnd(38)} -> ${String(got).padEnd(5)} (expected ${expected})  ${ok?"":"<<< "}${why}`);
}
console.log(`\n  ${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
