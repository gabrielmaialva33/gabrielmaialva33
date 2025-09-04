# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is Gabriel Maia's GitHub profile repository (username: gabrielmaialva33). It's not a traditional codebase but a personal profile showcase with automated statistics updates.

## Key Files

- **README.md** - The main GitHub profile content with animated elements, statistics, and professional information
- **.github/workflows/update-stats.yml** - GitHub Actions workflow that automatically updates Wakatime coding statistics daily
- **assets/** - Visual assets (SVG and PNG files) for profile branding

## Common Commands

### Update GitHub Statistics Manually
```bash
# Trigger the Wakatime stats update workflow manually
gh workflow run "Waka Readme"
```

### View Workflow Status
```bash
# Check the status of the automated stats update
gh run list --workflow=update-stats.yml
```

## Architecture

This repository uses:
- **GitHub Actions** for daily automated updates at 00:00 UTC
- **Wakatime API** integration for coding statistics
- **anmol098/waka-readme-stats@master** action for README updates
- Markdown with embedded HTML for rich profile formatting

## Important Considerations

1. **Secrets Required**: The workflow requires two secrets configured in repository settings:
   - `WAKATIME_API_KEY` - Wakatime API key for fetching coding statistics
   - `GH_TOKEN` - GitHub token with repo permissions for updating README

2. **README Structure**: The README contains placeholders that are automatically updated by the Wakatime action. These sections should not be manually edited as they will be overwritten.

3. **Asset Management**: Visual assets in the `assets/` directory are referenced in the README. Ensure paths remain consistent when updating or adding new assets.

4. **Workflow Schedule**: The stats update runs daily at midnight UTC. Manual triggers are also available via workflow_dispatch.