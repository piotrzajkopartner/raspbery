#!/usr/bin/env python3
import os
import glob
import csv
import time
import datetime

LOG_DIR = "/home/partner/monitoring"
PATTERN = "network_log_*.csv"
SPEEDTEST_LOG = "/home/partner/monitoring/speed_log.txt"
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


def read_last_speedtests(path, count=4):
    """Zwraca listę ostatnich 'count' linii ze speed_log.txt (od najnowszej)."""
    if not os.path.exists(path):
        return []
    try:
        lines = []
        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    lines.append(line)
        return lines[-count:][::-1]  # od najnowszej
    except Exception:
        return []


def read_ping_history(path, max_entries=100):
    """Zwraca historię pingów dla ROUTER/INTERNET.

    Zwracany format:
        {
          'ROUTER': [(ts, loss:int, latency:float, status:str), ...],
          'INTERNET': [...]
        }
    Liczymy maksymalnie max_entries najnowszych wpisów na target.
    """
    history = {"ROUTER": [], "INTERNET": []}
    if not os.path.exists(path):
        return history
    try:
        with open(path, newline="") as f:
            reader = csv.DictReader(f, delimiter=";")
            for row in reader:
                target = row.get("Target", "")
                if target not in history:
                    continue
                ts = row.get("Timestamp", "")
                try:
                    loss = int(float(row.get("Packet_Loss_% ", "0").replace(",", ".")))
                except Exception:
                    loss = 0
                try:
                    latency = float(row.get("Avg_Latency_ms", "0").replace(",", "."))
                except Exception:
                    latency = 0.0
                status = row.get("Status", "")
                history[target].append((ts, loss, latency, status))

        # ogranicz do max_entries od końca
        for key in history:
            if len(history[key]) > max_entries:
                history[key] = history[key][-max_entries:]
        return history
    except FileNotFoundError:
        return history


def status_to_color(status: str) -> str:
    if status == "OK":
        return COLOR_GREEN
    if status in ("WARN_LATENCY", "WARN_LOSS"):
        return COLOR_YELLOW
    if status in ("CRITICAL", "DOWN"):
        return COLOR_RED
    return COLOR_CYAN


def format_big_label(label: str) -> str:
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
        history = read_ping_history(latest, max_entries=100)

        def print_block(name):
            entries = history.get(name, [])
            if not entries:
                print(COLOR_RED + f"Brak danych o {name} w logu." + COLOR_RESET)
                return

            # ostatni wpis
            last_ts, last_loss, last_lat, last_status = entries[-1]
            color = status_to_color(last_status)
            label = f"{name}: {last_status}"

            print()
            print(color + format_big_label(label) + COLOR_RESET)
            print(f"Ostatni pomiar: {last_ts}  loss={last_loss}%  avg={last_lat:.1f} ms")

            # ostatnie 5 pomiarów
            print("  Ostatnie 5 pomiarów (od najnowszego):")
            for ts, loss, lat, st in reversed(entries[-5:]):
                print(f"    {ts}  loss={loss:3d}%  avg={lat:6.1f} ms  {st}")

            # średnie z ostatnich N (max 100)
            n = len(entries)
            avg_loss = sum(e[1] for e in entries) / n
            avg_lat = sum(e[2] for e in entries) / n
            print(f"  Średnie z ostatnich {n} pomiarów: loss={avg_loss:.1f}%  avg={avg_lat:.1f} ms")

        # Router i Internet
        print_block("ROUTER")
        print_block("INTERNET")

        print()
        print("Legenda:")
        print(COLOR_GREEN + "  OK" + COLOR_RESET + "            - brak problemów")
        print(COLOR_YELLOW + "  WARN_LATENCY/LOSS" + COLOR_RESET + " - opóźnienia lub utrata pakietów")
        print(COLOR_RED + "  CRITICAL/DOWN" + COLOR_RESET + "    - duże problemy lub całkowity brak łącza")

        print("".ljust(60, "-"))
        print(f"Źródło pingów : {latest}")

        # Ostatnie speedtesty
        st_lines = read_last_speedtests(SPEEDTEST_LOG, count=4)
        if st_lines:
            print("Ostatnie speedtesty (najnowsze u góry):")
            for line in st_lines:
                print(f"  {line}")
        else:
            print("Speedtest: brak danych (sprawdź crontab i speed_log.txt)")

        print(f"Odświeżanie co {REFRESH_SECONDS} s (Ctrl+C, aby wyjść)")

        time.sleep(REFRESH_SECONDS)


if __name__ == "__main__":
    main()
