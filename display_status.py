#!/usr/bin/env python3
import os
import glob
import csv
import time
import datetime

LOG_DIR = "/home/pi/monitoring"
PATTERN = "network_log_*.csv"
REFRESH_SECONDS = 5

# ANSI kolory
COLOR_RESET = "\033[0m"
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_RED = "\033[91m"
COLOR_CYAN = "\033[96m"


def find_latest_log_file():
    files = glob.glob(os.path.join(LOG_DIR, PATTERN))
    if not files:
        return None
    return max(files, key=os.path.getmtime)


def read_last_statuses(path):
    """Zwraca słownik: { 'ROUTER': (timestamp, status), 'INTERNET': (timestamp, status) }"""
    statuses = {}
    try:
        with open(path, newline="") as f:
            reader = csv.DictReader(f, delimiter=";")
            for row in reader:
                target = row.get("Target", "")
                ts = row.get("Timestamp", "")
                status = row.get("Status", "")
                if target in ("ROUTER", "INTERNET"):
                    statuses[target] = (ts, status)
    except FileNotFoundError:
        return {}
    return statuses


def status_to_color(status: str) -> str:
    if status == "OK":
        return COLOR_GREEN
    if status in ("WARN_LATENCY", "WARN_LOSS"):
        return COLOR_YELLOW
    if status in ("CRITICAL", "DOWN"):
        return COLOR_RED
    return COLOR_CYAN


def format_big_label(label: str) -> str:
    # Prosty "baner" tekstowy
    line = "=" * (len(label) + 4)
    return f"{line}\n| {label} |\n{line}"


def clear_screen():
    print("\033[2J\033[H", end="")


def main():
    while True:
        clear_screen()

        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"Raspberry Pi Network Probe - STATUS   ({now})")
        print("".ljust(60, "-"))

        latest = find_latest_log_file()
        if latest is None:
            print(COLOR_RED + "Brak plików logów. Upewnij się, że monitor.py działa." + COLOR_RESET)
            time.sleep(REFRESH_SECONDS)
            continue

        statuses = read_last_statuses(latest)

        # Router
        if "ROUTER" in statuses:
            ts, st = statuses["ROUTER"]
            color = status_to_color(st)
            label = f"ROUTER: {st}"
            print()
            print(color + format_big_label(label) + COLOR_RESET)
            print(f"Ostatni pomiar: {ts}")
        else:
            print(COLOR_RED + "Brak danych o ROUTERZE w logu." + COLOR_RESET)

        # Internet
        if "INTERNET" in statuses:
            ts, st = statuses["INTERNET"]
            color = status_to_color(st)
            label = f"INTERNET: {st}"
            print()
            print(color + format_big_label(label) + COLOR_RESET)
            print(f"Ostatni pomiar: {ts}")
        else:
            print(COLOR_RED + "Brak danych o INTERNECIE w logu." + COLOR_RESET)

        print()
        print("Legenda:")
        print(COLOR_GREEN + "  OK" + COLOR_RESET + "            - brak problemów")
        print(COLOR_YELLOW + "  WARN_LATENCY/LOSS" + COLOR_RESET + " - opóźnienia lub utrata pakietów")
        print(COLOR_RED + "  CRITICAL/DOWN" + COLOR_RESET + "    - duże problemy lub całkowity brak łącza")

        print("".ljust(60, "-"))
        print(f"Źródło: {latest}")
        print(f"Odświeżanie co {REFRESH_SECONDS} s (Ctrl+C, aby wyjść)")

        time.sleep(REFRESH_SECONDS)


if __name__ == "__main__":
    main()
