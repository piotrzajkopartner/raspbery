#!/usr/bin/env python3
import subprocess
import time
import datetime
import os
import configparser

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.ini")


def load_config():
    cfg = configparser.ConfigParser()
    cfg.read(CONFIG_FILE)

    network = cfg["network"]
    thresholds = cfg["thresholds"]

    return {
        "router_ip": network.get("router_ip", "192.168.0.1"),
        "internet_ip": network.get("internet_ip", "8.8.8.8"),
        "log_dir": network.get("log_dir", "/home/pi/monitoring"),
        "log_prefix": network.get("log_prefix", "network_log"),
        "ping_count": network.getint("ping_count", 5),
        "ping_interval_ms": network.getint("ping_interval_ms", 200),
        "interval_ok": network.getint("interval_ok", 60),
        "interval_problem": network.getint("interval_problem", 5),
        "latency_warn_ms": thresholds.getfloat("latency_warn_ms", 100.0),
        "loss_warn_percent": thresholds.getint("loss_warn_percent", 5),
        "loss_critical_percent": thresholds.getint("loss_critical_percent", 20),
    }


def get_log_file_path(cfg: dict) -> str:
    today = datetime.date.today().strftime("%Y-%m-%d")
    os.makedirs(cfg["log_dir"], exist_ok=True)
    return os.path.join(cfg["log_dir"], f"{cfg['log_prefix']}_{today}.csv")


def ensure_header(path: str):
    if not os.path.exists(path):
        with open(path, "w") as f:
            f.write("Timestamp;Target;Packet_Loss_%;;Avg_Latency_ms;Status\n")


def run_fping(target: str, count: int, interval_ms: int):
    """Zwraca (loss_percent:int, avg_latency_ms:float) lub (100, 0.0) przy błędzie."""
    try:
        cmd = [
            "fping",
            "-c",
            str(count),
            "-q",
            "-p",
            str(interval_ms),
            target,
        ]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10,
        )
        stderr = result.stderr.strip()

        if "xmt/rcv/%loss" not in stderr or "min/avg/max" not in stderr:
            return 100, 0.0

        try:
            part_loss = stderr.split("xmt/rcv/%loss =")[1].split(",")[0].strip()
            loss_str = part_loss.split("/")[-1].replace("%", "").strip()
            loss = int(loss_str)
        except Exception:
            loss = 100

        try:
            part_lat = stderr.split("min/avg/max =")[1].strip()
            avg_str = part_lat.split("/")[1].strip()
            avg = float(avg_str)
        except Exception:
            avg = 0.0

        return loss, avg
    except Exception:
        return 100, 0.0


def classify_status(loss: int, latency: float, cfg: dict) -> str:
    if loss == 100:
        return "DOWN"
    if loss >= cfg["loss_critical_percent"]:
        return "CRITICAL"
    if loss >= cfg["loss_warn_percent"]:
        return "WARN_LOSS"
    if latency >= cfg["latency_warn_ms"]:
        return "WARN_LATENCY"
    return "OK"


def main():
    cfg = load_config()
    print("Starting network monitor...")
    print(f"Router IP   : {cfg['router_ip']}")
    print(f"Internet IP : {cfg['internet_ip']}")
    print(f"Log dir     : {cfg['log_dir']}")

    while True:
        log_file = get_log_file_path(cfg)
        ensure_header(log_file)

        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        r_loss, r_lat = run_fping(
            cfg["router_ip"],
            cfg["ping_count"],
            cfg["ping_interval_ms"],
        )
        r_status = classify_status(r_loss, r_lat, cfg)

        i_loss, i_lat = run_fping(
            cfg["internet_ip"],
            cfg["ping_count"],
            cfg["ping_interval_ms"],
        )
        i_status = classify_status(i_loss, i_lat, cfg)

        with open(log_file, "a") as f:
            f.write(f"{now_str};ROUTER;{r_loss};{r_lat:.2f};{r_status}\n")
            f.write(f"{now_str};INTERNET;{i_loss};{i_lat:.2f};{i_status}\n")

        if (r_status == "OK" and i_status == "OK"):
            sleep_sec = cfg["interval_ok"]
        else:
            sleep_sec = cfg["interval_problem"]

        time.sleep(sleep_sec)


if __name__ == "__main__":
    main()
