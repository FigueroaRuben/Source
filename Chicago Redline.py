from datetime import datetime, timedelta
import argparse
import os
import sys
import pandas as pd
import requests


#!/usr/bin/env python3
"""
Chicago Redline run counter (last 5 days)

This script counts how many times the Chicago "Red Line" ran in the past 5 days
based on either:
 - a local CSV file with timestamped events, or
 - a Socrata dataset on data.cityofchicago.org (SODA API).

Usage examples:
        python "Chicago Redline.py" --csv events.csv --date-col event_time --line-col line --line-value "Red Line"
        python "Chicago Redline.py" --socrata --dataset-id YOUR_DATASET_ID --date-col date --line-col line_name

If using Socrata, set SODA_APP_TOKEN environment variable if you have one.
"""


# dependency check removed: imports are at the top of the file


def count_from_csv(path, date_col, line_col, line_value):
                df = pd.read_csv(path)
                if date_col not in df.columns or line_col not in df.columns:
                                raise ValueError("CSV does not contain the specified columns.")
                df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
                now = pd.Timestamp.utcnow()
                cutoff = now - pd.Timedelta(days=5)
                mask = df[date_col].notna() & (df[date_col] >= cutoff) & (df[date_col] <= now)
                # compare line values case-insensitively
                mask = mask & df[line_col].astype(str).str.lower().eq(str(line_value).lower())
                return int(mask.sum())


def count_from_socrata(domain, dataset_id, date_col, line_col, line_value, app_token=None):
                now = datetime.utcnow()
                cutoff = now - timedelta(days=5)
                # Socrata expects ISO datetimes; use full-day range
                start_iso = cutoff.strftime("%Y-%m-%dT%H:%M:%S")
                end_iso = now.strftime("%Y-%m-%dT%H:%M:%S")
                # Build SoQL where clause. Use single quotes around values.
                where = f"{date_col} >= '{start_iso}' AND {date_col} <= '{end_iso}' AND lower({line_col}) = '{str(line_value).lower()}'"
                params = {"$select": "count(*)"}
                params["$where"] = where
                url = f"https://{domain}/resource/{dataset_id}.json"
                headers = {}
                if app_token:
                                headers["X-App-Token"] = app_token
                r = requests.get(url, params=params, headers=headers, timeout=30)
                r.raise_for_status()
                data = r.json()
                if not data:
                                return 0
                # Socrata returns count as string in "count"
                count = int(data[0].get("count", 0))
                return count


def main():
                p = argparse.ArgumentParser(description="Count Red Line runs in last 5 days from CSV or Socrata dataset.")
                grp = p.add_mutually_exclusive_group(required=True)
                grp.add_argument("--csv", help="Path to CSV file with events")
                grp.add_argument("--socrata", action="store_true", help="Query Socrata API (data.cityofchicago.org)")
                p.add_argument("--dataset-id", help="Socrata dataset id (required for --socrata)")
                p.add_argument("--domain", default="data.cityofchicago.org", help="Socrata domain (default data.cityofchicago.org)")
                p.add_argument("--date-col", required=True, help="Name of the timestamp column (CSV or Socrata)")
                p.add_argument("--line-col", required=True, help="Name of the line/route column (CSV or Socrata)")
                p.add_argument("--line-value", default="Red Line", help="Value to match for the line (default 'Red Line')")
                args = p.parse_args()

                try:
                                if args.csv:
                                                count = count_from_csv(args.csv, args.date_col, args.line_col, args.line_value)
                                else:
                                                if not args.dataset_id:
                                                                p.error("--dataset-id is required with --socrata")
                                                app_token = os.environ.get("SODA_APP_TOKEN")
                                                count = count_from_socrata(args.domain, args.dataset_id, args.date_col, args.line_col, args.line_value, app_token)
                except Exception as e:
                                print("Error:", e)
                                sys.exit(1)

                print(count)


if __name__ == "__main__":
                main()