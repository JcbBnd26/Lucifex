# Output

Operational outputs from the running application. Generated files, exported reports, temporary artifacts.

## Why this folder is gitignored

The `.gitignore` excludes everything in `output/` EXCEPT this README. The folder is for runtime artifacts, not source. Tracking generated content in git pollutes history and bloats the repo.

The README is tracked so the folder exists in the repo (git doesn't track empty folders) and so contributors understand what the folder is for.
