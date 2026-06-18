# n8n Loop Runner — Setup (Intel Mac, Docker)

## 1. Start n8n locally

```bash
docker run -it --rm \
  -p 5678:5678 \
  -e N8N_BASIC_AUTH_ACTIVE=false \
  -e CONRAD_API_URL=http://host.docker.internal:8001 \
  -e NOTEBOOKLM_NOTEBOOK_ID=corpora/your-corpus-id \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n
```

Open http://localhost:5678

## 2. Import the workflow

In n8n UI: Settings → Import from File → select `conrad_loop.workflow.json`

## 3. Set environment variables in n8n

Add to the `docker run` command (or n8n Settings → Environment):
- `CONRAD_API_URL` — URL of the running MCP bridge (default: `http://host.docker.internal:8001`)
- `NOTEBOOKLM_NOTEBOOK_ID` — your corpus resource name (`corpora/...`)

## 4. Start the MCP bridge

```bash
cd /Users/christopheramoore/dev/expo-os/mcp_bridge
pip install -r requirements.txt
cp .env.example .env   # fill in your keys
uvicorn server:app --port 8001
```

## 5. Run the loop

Trigger manually in n8n UI, or fire via webhook.
The loop: Manual Trigger → /conrad → Format lesson → Write to VaultSpace → Respond.
Check VaultSpace writes: `mongosh expo_os --eval "db.vaultspace.find().sort({ts:-1}).limit(5)"`
