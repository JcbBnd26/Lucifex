# Infra

Infrastructure and deployment configuration. The foundation that runs the application.

## Internal organization

| Folder | Purpose |
|--------|---------|
| `docker/` | Dockerfiles for backend, frontend, and worker processes. |
| `deployment/` | Configuration for the hosting platform (Railway, Fly.io, Render). |
| `github-actions/` | CI/CD workflows. |
| `scripts/` | One-off operational scripts. |

## Why infra is separate

Deployment is not application logic. The instructions for "how to run this on a server" are different from the application itself. Mixing them creates lock-in to specific environments and confuses contributors about what is the app vs what is the plumbing.
