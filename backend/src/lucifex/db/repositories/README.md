# Repositories

Query helpers grouped by table or domain.

## Purpose

Common queries deserve a single home. "Get all clips pending review for channel X." "Find posts from the last 7 days with their analytics." Without repositories, the same query gets written five different ways in five different services.

## When to add a repository

When a query is needed in more than one place, or when a query is non-trivial enough to deserve a name. Don't preemptively wrap every simple `get_by_id` — that's bloat.

## Convention

`repositories/clips.py` for clip queries. `repositories/posts.py` for post queries. Each function takes a session and parameters; returns models or DTOs.
