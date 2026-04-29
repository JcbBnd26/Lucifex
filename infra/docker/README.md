# Docker

Dockerfiles describe how to build container images for the backend, frontend, and worker processes.

## Planned files

- `backend.Dockerfile` — builds the FastAPI server image
- `worker.Dockerfile` — builds the worker image (often the same as backend with a different entrypoint)
- `frontend.Dockerfile` — builds the Next.js production image

## Why containers

A container image is built once and runs identically in development, staging, and production. No "works on my machine" problems. The Dockerfile is the recipe; the image is the meal.
