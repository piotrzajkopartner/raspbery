# Raspberry Pi Network Probe

Prosta sonda sieciowa na Raspberry Pi:

- monitoruje ping do **routera** i **Internetu**,
- loguje wyniki do plików CSV (łatwe w Excelu),
- cyklicznie robi `speedtest-cli`,
- startuje automatycznie po podłączeniu zasilania (systemd).

## Wymagania

- Raspberry Pi z Raspberry Pi OS,
- użytkownik `pi`,
- dostęp do Internetu,
- `git` (do klonowania repozytorium).

## Instalacja

Na Raspberry Pi:

```bash
cd /home/pi
git clone https://github.com/TWOJ_USER/raspi-net-probe.git
cd raspi-net-probe
chmod +x setup.sh
./setup.sh
```

## Konfiguracja

Edytuj plik `config.ini`:

- `router_ip` – IP routera (np. `192.168.0.1`),
- `internet_ip` – docelowy host w Internecie (np. `8.8.8.8`),
- progi ostrzeżeń w sekcji `[thresholds]`.

Po zmianie konfiguracji:

```bash
sudo systemctl restart net-probe.service
```

## Gdzie są logi?

- katalog: `/home/pi/monitoring`
- pliki:
  - `network_log_YYYY-MM-DD.csv` – ping do routera i Internetu,
  - `speed_log.txt` – wyniki `speedtest-cli` (co godzinę).

Format CSV:

```text
Timestamp;Target;Packet_Loss_%;;Avg_Latency_ms;Status
```

- `Target` – `ROUTER` lub `INTERNET`,
- `Status` – `OK`, `WARN_LATENCY`, `WARN_LOSS`, `CRITICAL`, `DOWN`.

## Analiza logów

Na Raspberry Pi:

```bash
cd /home/pi/raspi-net-probe
python3 analyze_logs.py
```

Wyświetli podsumowanie statusów i przedziały czasowe problemów.

Możesz też skopiować pliki CSV na komputer i otworzyć w Excelu.
