#!/usr/bin/env python3
import argparse
import os
from datetime import datetime, timedelta

# Ensure local src is importable when running from repo root
import sys
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_path = os.path.join(repo_root, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from power_profiling import IDRACRemoteClient, IDRACQueryParams


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Demo: query iDRAC out-of-band power via REPACSS submodule')
    parser.add_argument('--db-host', default=os.getenv('REPACSS_DB_HOST', ''), help='DB host (TimescaleDB reachable via SSH tunnel)')
    parser.add_argument('--db-port', type=int, default=int(os.getenv('REPACSS_DB_PORT', '5432')), help='DB port')
    parser.add_argument('--database', default=os.getenv('REPACSS_DATABASE', 'h100'), help='Database name (e.g., h100, zen4, infra)')
    parser.add_argument('--db-user', default=os.getenv('REPACSS_DB_USER', ''), help='DB user')
    parser.add_argument('--db-password', default=os.getenv('REPACSS_DB_PASSWORD', ''), help='DB password')
    parser.add_argument('--ssh-hostname', default=os.getenv('REPACSS_SSH_HOST', ''), help='SSH hostname')
    parser.add_argument('--ssh-port', type=int, default=int(os.getenv('REPACSS_SSH_PORT', '22')), help='SSH port')
    parser.add_argument('--ssh-username', default=os.getenv('REPACSS_SSH_USER', ''), help='SSH username')
    parser.add_argument('--ssh-key', default=os.getenv('REPACSS_SSH_KEY', ''), help='SSH private key path')
    parser.add_argument('--ssh-passphrase', default=os.getenv('REPACSS_SSH_PASSPHRASE', ''), help='SSH key passphrase')
    parser.add_argument('--schema', default=os.getenv('REPACSS_SCHEMA', 'idrac'), help='Schema to query (default: idrac)')
    parser.add_argument('--node-id', default=os.getenv('REPACSS_NODE_ID', None), help='Optional node id filter')
    parser.add_argument('--hours', type=int, default=int(os.getenv('REPACSS_LOOKBACK_HOURS', '1')), help='Lookback hours window')
    parser.add_argument('--limit', type=int, default=int(os.getenv('REPACSS_LIMIT', '50')), help='Max records if no time range')
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if not (args.db_host and args.db_user and args.db_password and args.ssh_hostname and args.ssh_username and args.ssh_key):
        print('Missing required connection parameters. Provide via CLI flags or environment variables:')
        print('  REPACSS_DB_HOST, REPACSS_DB_PORT, REPACSS_DATABASE, REPACSS_DB_USER, REPACSS_DB_PASSWORD')
        print('  REPACSS_SSH_HOST, REPACSS_SSH_PORT, REPACSS_SSH_USER, REPACSS_SSH_KEY, REPACSS_SSH_PASSPHRASE')
        raise SystemExit(2)

    client = IDRACRemoteClient(
        db_host=args.db_host,
        db_port=args.db_port,
        database=args.database,
        db_user=args.db_user,
        db_password=args.db_password,
        ssh_hostname=args.ssh_hostname,
        ssh_port=args.ssh_port,
        ssh_username=args.ssh_username,
        ssh_private_key_path=args.ssh_key,
        ssh_passphrase=args.ssh_passphrase,
        schema=args.schema,
    )

    start_time = datetime.utcnow() - timedelta(hours=args.hours)
    end_time = datetime.utcnow()
    params = IDRACQueryParams(node_id=args.node_id, start_time=start_time, end_time=end_time, limit=args.limit)

    with client:
        rows = client.fetch_computepower(params)
        print(f"Fetched {len(rows)} computepower rows. Showing up to 5:")
        for row in rows[:5]:
            print(row)

        temps = client.fetch_boardtemperature(params)
        print(f"Fetched {len(temps)} boardtemperature rows. Showing up to 5:")
        for row in temps[:5]:
            print(row)

        print('Cluster summary:')
        print(client.summary_cluster())


if __name__ == '__main__':
    main()


