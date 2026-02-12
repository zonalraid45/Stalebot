# Engine

Engines are uploaded here.

## Recent bot timing + blunder-guard features

If you merged the latest commits, these are now active in the bot:

- `time_multiplier`: bot can *pretend* it has less clock than shown.
  - Example: `1+0` with `time_multiplier: 3` applies a virtual `3s` penalty from available time budgeting.
- `blunder_guard_min_think_ms`: minimum target think time for each move (only when safe on clock).
- `blunder_guard_verify_ratio`: enables a second verification search using extra budget.
- `blunder_guard_min_verify_ms`: floor for verification search time.

### Blunder feature concept (simple)

1. Bot computes a safe main think time from remaining clock + increment.
2. Bot searches once and gets a candidate move.
3. If verification is enabled and extra safe budget exists, bot searches again.
4. If second search disagrees, bot plays the verified move.

This helps avoid quick tactical blunders while still respecting time safety.

## Config keys in `settings.yml`

- `move_time_ms`
- `time_multiplier` (also accepts typo fallbacks `timemultier`/`timemuliter` in code)
- `blunder_guard_min_think_ms`
- `blunder_guard_verify_ratio`
- `blunder_guard_min_verify_ms`
