# GitHub Wiki Migration

This directory contains the prepared documentation files for migration to GitHub Wiki.

## Migration Steps

1. **Enable Wiki** in your GitHub repository settings:
   - Go to your repository on GitHub
   - Click "Settings" tab
   - Scroll down to "Features" section
   - Check "Wikis" to enable

2. **Clone the Wiki Repository**:

   ```bash
   git clone https://github.com/tears-mysthrala/Oroitz.wiki.git
   cd Oroitz.wiki
   ```

3. **Copy Wiki Files**:
   - Copy all `.md` files from this `Oroitz.wiki/` directory to your cloned wiki repository
   - The files are already named according to GitHub Wiki conventions

4. **Commit and Push**:

   ```bash
   git add .
   git commit -m "Migrate documentation to GitHub Wiki"
   git push origin master
   ```

5. **Verify**:
   - Visit [https://github.com/tears-mysthrala/Oroitz/wiki](https://github.com/tears-mysthrala/Oroitz/wiki) to see your wiki
   - The Home.md file will be the wiki homepage

## File Mapping

| Original File | Wiki Page |
|---------------|-----------|
| docs/user-guides/getting-started.md | Getting-Started |
| docs/user-guides/cli-guide.md | CLI-Guide |
| docs/user-guides/gui-guide.md | GUI-Guide |
| docs/user-guides/tui-guide.md | TUI-Guide |
| docs/user-guides/workflow-reference.md | Workflow-Reference |
| docs/user-guides/troubleshooting.md | Troubleshooting |
| docs/volatility-wrapper-spec.md | Product-Specification |
| docs/core-engine-spec.md | Core-Engine-Details |
| docs/tui-spec.md | TUI-Plan |
| docs/gui-spec.md | GUI-Plan |
| docs/workflows-and-plugins.md | Workflow-Catalog |
| docs/project-structure-guide.md | Project-Structure-Guide |
| docs/development-plan.md | Development-Plan |
| docs/release-checklist.md | Release-Checklist |
| docs/adrs/ADR-0001-*.md | ADR-0001-Language-and-Runtime |
| docs/adrs/ADR-0002-*.md | ADR-0002-Dependency-and-Volatility-Integration |
| docs/adrs/ADR-0003-*.md | ADR-0003-Interface-Tooling |
| docs/adrs/ADR-0004-*.md | ADR-0004-Retry-and-Fallback |

## Notes

- All internal links within the documentation may need updating to use wiki links
- The README.md in the main repository has been updated to link to the wiki pages
- The ROADMAP.md remains in the main repository for GitHub Projects integration
