# OpenIpico

**Open source timing software for IPICO Sports RFID timing readers.**

> This project aims to build an open, community-driven alternative to the proprietary iPicoWiz software for managing IPICO Sports timing hardware at triathlons and running events.

## Supported Hardware

| Reader | Ports | Status |
|--------|-------|--------|
| IPICO Super Elite Reader | 10000, 10200, 10201 | ✅ Tested |
| IPICO Elite Reader | 10000, 10200, 10201 | ✅ Tested |
| IPICO Lite Reader | 10000, 10200, 10201 | ✅ Expected |
| IPICO Lite+ Reader | 10000, 10200, 10201 | ✅ Expected |

## Features

- [x] Connect to IPICO readers via TCP/IP (Ethernet/UTP)
- [x] Receive raw tag stream (port 10000)
- [x] Receive First-Seen / Last-Seen data (port 10200)
- [x] Parse IP-X protocol tag records
- [ ] Split/lap time calculation
- [ ] Web dashboard for live timing
- [ ] Race registration integration
- [ ]结果 export (CSV, JSON, PDF)
- [ ] Tag pass adjustment (shift a reading to the correct timing point)
- [ ] Docker deployment

## Quick Start

```bash
# Connect to a reader and stream raw tag data
python3 reader_client.py --host 192.168.1.100 --port 10000

# Use First-Seen / Last-Seen mode (recommended for timing)
python3 reader_client.py --host 192.168.1.100 --port 10200
```

## Protocol

The IPICO IP-X protocol is documented in [PROTOCOL.md](PROTOCOL.md).

## Architecture

```
IPICO Reader (hardware)
    |
    |--- TCP/IP (Ethernet/UTP cable)
    |
OpenIpico Software
    |
    |--- Tag Parser (IP-X protocol)
    |--- Race Logic (splits, laps, finish times)
    |--- Web UI (live results)
    |
Results (CSV, JSON, live display)
```

## License

MIT License — see [LICENSE](LICENSE)
