import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = str(ROOT / "src")
if SRC_PATH not in sys.path:
    sys.path.append(SRC_PATH)

from mental_health_screening.storage import (  # noqa: E402
    create_database_backup,
    get_database_metadata,
    list_audit_logs,
    list_backup_runs,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Admin utility for PostgreSQL-backed storage.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("metadata", help="Show database, encryption, audit, and backup metadata.")

    audit_parser = subparsers.add_parser("audit", help="Show recent audit log entries.")
    audit_parser.add_argument("--limit", type=int, default=20, help="Maximum number of audit rows to print.")

    backups_parser = subparsers.add_parser("backups", help="Show recent backup runs.")
    backups_parser.add_argument("--limit", type=int, default=20, help="Maximum number of backup rows to print.")

    backup_parser = subparsers.add_parser("backup", help="Create an encrypted backup artifact.")
    backup_parser.add_argument("--output-path", default=None, help="Optional explicit output path for the encrypted backup.")
    backup_parser.add_argument(
        "--exclude-audit-logs",
        action="store_true",
        help="Skip audit logs in the backup payload.",
    )

    args = parser.parse_args()
    if args.command == "metadata":
        payload = get_database_metadata()
    elif args.command == "audit":
        payload = list_audit_logs(limit=args.limit)
    elif args.command == "backups":
        payload = list_backup_runs(limit=args.limit)
    else:
        payload = create_database_backup(
            output_path=args.output_path,
            actor="storage_admin_cli",
            include_audit_logs=not args.exclude_audit_logs,
        )

    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
