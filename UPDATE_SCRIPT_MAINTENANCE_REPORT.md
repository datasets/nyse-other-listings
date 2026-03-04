# Update Script Maintenance Report

Date: 2026-03-04

- Re-ran `scripts/process.py` and refreshed:
  - `data/other-listed.csv`
  - `data/nyse-listed.csv`
  - `datapackage.json`
- Updated GitHub Actions workflow automation:
  - corrected workflow name,
  - removed push/PR triggers and kept schedule + manual dispatch,
  - added explicit `permissions: contents: write`,
  - upgraded to `actions/checkout@v4` and `actions/setup-python@v5`,
  - restricted commit scope to data and datapackage outputs.
