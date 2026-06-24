# BCA Command Library

Reusable GitHub Copilot prompts and instructions for Blue Collar Apps projects.

## Recommended Use

1. Copy `.github/copilot-instructions.md` into the root of any BCA repository.
2. Copy `docs/Prompts/BCA_Master_Analysis_Prompt.md` into the repository.
3. In GitHub Copilot Chat, paste:

```text
Read the entire repository. Then follow the instructions in docs/Prompts/BCA_Master_Analysis_Prompt.md and generate the full report.
```

4. Save Copilot's completed report in:

```text
docs/Reports/YYYY-MM-DD_BCA_Repository_Analysis.md
```

## Folder Structure

- `Repository-Analysis/` — full repository review prompts
- `Architecture/` — system, database, API, and deployment prompts
- `Launch/` — launch and production-readiness prompts
- `Marketing/` — market and monetization prompts
- `AI-Agents/` — agent architecture prompts
- `Captain-Culinary/` — Captain Culinary-specific prompts
- `Second-Brain/` — BCA Second Brain prompts
- `Revenue/` — revenue, SaaS, subscription, and token-economy prompts
- `.github/copilot-instructions.md` — permanent Copilot instructions
- `docs/Prompts/BCA_Master_Analysis_Prompt.md` — master mega prompt
- `docs/Reports/` — store generated repository reports

## Current Drop

This `/today` folder is a working command-library drop for Blue Collar Apps. It can be copied into any BCA repository or promoted into the repository root later.
