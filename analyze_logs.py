#!/usr/bin/env python3
import os
import glob
import csv
from collections import Counter

LOG_DIR = "/home/partner/monitoring"
PATTERN = "network_log_*.csv"


def main():
    files = sorted(glob.glob(os.path.join(LOG_DIR, PATTERN)))
    if not files:
        print("Brak plików logów.")
        return

    status_counts = Counter()
    first_problem = None
    last_problem = None

    for path in files:
        with open(path, newline="") as f:
            reader = csv.DictReader(f, delimiter=";")
            for row in reader:
                status = row["Status"]
                status_counts[status] += 1

                if status != "OK":
                    ts = row["Timestamp"]
                    if first_problem is None:
                        first_problem = ts
                    last_problem = ts

    print("Podsumowanie statusów:")
    for status, cnt in status_counts.items():
        print(f"  {status:13s}: {cnt}")

    if first_problem:
        print(f"\nPierwszy zarejestrowany problem: {first_problem}")
        print(f"Ostatni zarejestrowany problem : {last_problem}")
    else:
        print("\nBrak zarejestrowanych problemów (same OK).")


if __name__ == "__main__":
    main()
