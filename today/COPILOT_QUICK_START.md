# GitHub Copilot Quick Start for BCA

## Fastest Method

Open the repository in VS Code or GitHub Codespaces.

Open Copilot Chat and paste:

```text
Read the entire repository. Then follow the instructions below exactly.

[Paste the full BCA Master Analysis Prompt here]
```

## Better Method

Place these files in the repository:

```text
.github/copilot-instructions.md
docs/Prompts/BCA_Master_Analysis_Prompt.md
docs/Reports/
```

Then paste this into Copilot Chat:

```text
Read the entire repository. Follow docs/Prompts/BCA_Master_Analysis_Prompt.md. Save the resulting analysis as docs/Reports/BCA_Repository_Analysis.md.
```

## Best Long-Term Method

Keep this entire BCA Command Library as its own repository and copy the prompt files into each BCA app repo as needed.

## /today Use

This repository currently stores the working BCA Copilot package under `/today`. Use `/today/docs/Prompts/BCA_Master_Analysis_Prompt.md` as the master prompt source.
