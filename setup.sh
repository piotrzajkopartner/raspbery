#!/usr/bin/env bash
set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
USER_NAME="partner"
SERVICE_NAME="net-probe.service"

echo "[1/5] Instalacja pakietów (fping, speedtest-cli)..."
sudo apt update
sudo apt install -y fping speedtest-cli

echo "[2/5] Tworzenie katalogu na logi..."
MONITOR_DIR="/home/${USER_NAME}/monitoring"
sudo -u "${USER_NAME}" mkdir -p "${MONITOR_DIR}"

echo "[3/5] Kopiowanie pliku usługi systemd..."
sudo cp "${REPO_DIR}/${SERVICE_NAME}" /etc/systemd/system/${SERVICE_NAME}
sudo systemctl daemon-reload
sudo systemctl enable ${SERVICE_NAME}
sudo systemctl restart ${SERVICE_NAME}

echo "[4/5] (POMIŃ AUTOMATYCZNIE) Dodawanie wpisu do crontaba dla speedtest-cli..."
echo "    Dodaj ręcznie w crontab (crontab -e) taki wpis dla użytkownika partner:"
echo "    0 * * * * echo \"$(date +%Y-%m-%d_%H:%M);$(speedtest-cli --simple | tr '\n' ';' )\" >> /home/partner/monitoring/speed_log.txt"

echo "[5/5] Gotowe. Status usługi:"
systemctl status ${SERVICE_NAME} --no-pager || true
