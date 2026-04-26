# Chunks

Build-step prompt documents for Lucifex. Each chunk is a focused, executable unit of work for the code agent. Chunks are numbered and named.

Chunks are reference material — they are read by the code agent to perform a build step. After execution, they remain in the repository as documentation of how the project was built.

## Convention

- Chunk filenames follow the pattern: `chunk_{letter}_{slug}.md` (e.g., `chunk_a_initial_setup.md`).
- Each chunk is self-contained — the code agent should not need additional context outside the project to execute it.
- Each chunk ends with a git commit naming the chunk.
