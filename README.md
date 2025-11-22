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
cd /home/partner
git clone https://github.com/piotrzajkopartner/raspbery.git
cd raspbery
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

- katalog: `/home/partner/monitoring`
- pliki:
  - `network_log_YYYY-MM-DD.csv` – ping do routera i Internetu,
  - `speed_log.txt` – wyniki `speedtest-cli` (co 5 minut).

Format CSV:

```text
Timestamp;Target;Packet_Loss_% ;Avg_Latency_ms;Status
```

- `Target` – `ROUTER` lub `INTERNET`,
- `Status` – `OK`, `WARN_LATENCY`, `WARN_LOSS`, `CRITICAL`, `DOWN`.

## Analiza logów

Na Raspberry Pi:

```bash
cd /home/partner/raspbery
python3 analyze_logs.py
```

## Wyświetlanie statusu na monitorku (display_status.py)

Jeżeli Raspberry Pi ma podłączony monitorek (HDMI lub mały ekran), możesz uruchomić prosty dashboard statusu:

```bash
cd /home/partner/raspbery
chmod +x display_status.py   # tylko raz, jeśli potrzeba
python3 display_status.py
```

Skrypt:

- co kilka sekund odczytuje **ostatnie wpisy** z najnowszego pliku `network_log_YYYY-MM-DD.csv`,
- pokazuje duży, kolorowy status dla:
  - `ROUTER` – stan lokalnej sieci / połączenia z routerem,
  - `INTERNET` – stan połączenia z Internetem.

Kolory:

- zielony – `OK` (brak problemów),
- żółty – `WARN_LATENCY` / `WARN_LOSS` (opóźnienia lub umiarkowana utrata pakietów),
- czerwony – `CRITICAL` / `DOWN` (duże problemy lub całkowity brak łącza).

Zatrzymanie: `Ctrl+C`.

## Speedtest co 5 minut (crontab)

Aby `speedtest-cli` działał co 5 minut i dopisywał wyniki do `speed_log.txt`, dodaj wpis w cronie użytkownika `partner`:

```bash
crontab -e
```

Na końcu pliku dodaj linię:

```cron
*/5 * * * * echo "$(date +%Y-%m-%d_%H:%M);$(speedtest-cli --simple | tr '\n' ';' )" >> /home/partner/monitoring/speed_log.txt
```

Wyświetli podsumowanie statusów i przedziały czasowe problemów.

Możesz też skopiować pliki CSV na komputer i otworzyć w Excelu.
