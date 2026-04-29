# Frontend

The Lucifex frontend. Next.js with React. The dashboard and agent chat interface.

## Internal organization

| Folder | Purpose |
|--------|---------|
| `app/` | Next.js routes (file-based routing). |
| `components/` | Reusable generic UI primitives (buttons, inputs, modals). |
| `features/` | Feature-specific code grouped by domain. |
| `lib/` | API client, utilities, custom hooks. |
| `styles/` | Tailwind config and design tokens. |
| `public/` | Static assets. |
| `tests/` | Frontend tests. |

## Architectural principle

Pages depend on features. Features depend on components and `lib`. Components and `lib` depend on nothing else in the project. Dependencies flow one direction.
