# Components

Reusable generic UI primitives.

## What lives here

Generic components used across features. Buttons, inputs, modals, cards, tables, tooltips. Things with no business meaning, only visual purpose.

## What does NOT live here

Specific components like `ClipReviewCard` or `CampaignDashboard`. Those go in `features/`.

## Generic vs specific

`components/Button.tsx` — generic. Lives here.
`features/clips/ClipReviewCard.tsx` — specific. Lives in features.

Mixing these is how component folders become 200-file dumping grounds.
