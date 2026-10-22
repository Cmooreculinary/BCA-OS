---
name: cloudflare-dns-records
description: Add DNS records (CNAME, TXT, MX, A) to a Cloudflare domain in the browser when Chef pastes a list of records from Clerk, email or any service.
---

# Cloudflare DNS records

**Goal:** every record Chef lists is in Cloudflare, exactly as given, verified, with nothing else changed.

## Rules
- Chef's request with the list = permission to add those records only. Editing or deleting an existing record needs a separate yes.
- Never touch bcappz.com's existing website, MX or email records.
- Sign-in, email and verification records (Clerk, DKIM, mail, `_domainkey`, TXT) are **DNS only** (gray cloud). Proxy only if Chef says so.
- Name field gets the short name (`clerk`, not `clerk.bcappz.com`).

## Steps
1. Open dash.cloudflare.com → the domain → DNS → Records. Blank page: reload.
2. Search each name first. Exact match (same type, name and value) → already done, skip it. Same name with a different value → stop and ask Chef.
3. Note the count ("You have used N of 200").
4. Each remaining record: Add record → wait for the dialog → set Type (confirm it took) → turn proxy off **before** typing → Name → Target → check the values → Save.
5. Verify: count rose by exactly the number added (skipped ones add 0); read each full Name and Content (the table truncates) and compare character by character.
6. Report a short table (Name, Points to, Proxy) and the next step (e.g. "click Verify in Clerk; DNS can take up to an hour").
