# Scripts

One-off operational scripts. Things you run occasionally that aren't part of the main app flow.

## Examples (planned)

- `backup_db.sh` — back up the production database
- `seed_dev.py` — populate a development database with test data
- `migrate_storage.py` — move storage from one provider to another (if ever needed)
- `rotate_keys.py` — rotate encryption keys

## Convention

Each script should be runnable standalone with a clear purpose at the top. Destructive scripts should require confirmation flags (`--yes-really`).
