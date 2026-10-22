---
name: app-go-live
description: Take a BCA app from "code passes" to live on Chef's phone — Clerk sign-in, DNS, GitHub settings, Fly.io backend, Cloudflare frontend, launch checks.
---

# App go-live

**Goal:** Chef opens the app on his phone, signs in, and sees real data.

## Rules
- The app's own `DEPLOY.md` is the source of truth for names and order. Read it first.
- Chef enters every password, secret and key. Agents enter public values only.
- Chef OKs each deploy, DNS change and merge. Keep the app's approved look (e.g. Venue IQ keeps its v0 style).
- Fly + SQLite: one machine, one volume. Never scale up.

## Steps
1. **Status:** last deploy runs, which GitHub variables/secrets exist, does `https://<backend>/health` answer. Report VERIFIED vs INFERRED.
2. **Clerk:** Chef signs in. Get the publishable key and Frontend API URL. Add Clerk's DNS records with `cloudflare-dns-records`.
3. **GitHub settings** (repo → Settings → Secrets and variables → Actions): add the missing variables from DEPLOY.md. Secrets go in as secrets, by Chef. GitHub may ask Chef to confirm on his phone.
4. **Backend:** with Chef's OK, run "Deploy backend to Fly.io". Confirm `/health` is ok.
5. **Frontend:** with Chef's OK, re-run "Deploy to Cloudflare". If it fails, open the failed step and fix the cause.
6. **Launch checks:** run every check in DEPLOY.md and record results with dates.
7. **Chef phone test:** short numbered steps. Done only when he confirms it works.
