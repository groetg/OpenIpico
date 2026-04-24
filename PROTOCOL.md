# IPICO IP-X Protocol Documentation

This document describes the IPICO Sports IP-X protocol used by IPICO timing readers to transmit tag data over TCP/IP.

**Source:** Reverse-engineered from IPICO Elite Reader User Manual v2.4 (December 2009) and confirmed from IPICO Super Elite Reader manual (June 2016). Protocol details are based on published manual content.

---

## Ports

IPICO readers expose timing data via Telnet on these TCP ports:

| Port | Name | Description |
|------|------|-------------|
| `10000` | Raw Streaming | Every successful tag read |
| `10200` | First-Seen / Last-Seen | FS/LS truncated records |
| `10201` | XML | Same as 10200 but in XML format |
| `9999` | Control | Reader configuration, time sync |
| `9998` | Maintenance | Tuning reports, diagnostics |

Connect using: `telnet <reader-ip> <port>` or use the Python client.

---

## Tag Record Format (Raw — Port 10000)

Each tag pass produces a 36-character record:

```
aa000580017164f000010809271129024084
```

**Breakdown:**

| Position | Length | Field | Example | Description |
|----------|--------|-------|---------|-------------|
| 1-2 | 2 | Record Prefix | `aa` | Always `aa` = tag record |
| 3-14 | 12 | Tag ID | `0580017164f0` | Unique RFID tag ID |
| 15-30 | 16 | Date/Time/IRQ | `00010809271129024084` | See below |
| 31-36 | 6 | LRC Checksum | `080840` | Longitudinal Redundancy Check |

### Tag ID Format

- Always 12 hexadecimal characters
- Always starts with `058`
- `058xxxx` = IPICO Sportag series
- Example: `0580017164f0`

### Date/Time Sub-fields

Within positions 15-30:

```
MM DD YY HH MM SS MS
00010809271129024084
^^ ^^YY ^^ ^^ ^^ ^^
```

| Sub-field | Length | Position | Example | Meaning |
|-----------|--------|----------|---------|---------|
| Month | 2 | 3-4 | `08` | August |
| Day | 2 | 5-6 | `09` | 9th |
| Year | 2 | 7-8 | `27` | 2027 |
| Hour | 2 | 9-10 | `11` | 11:00 |
| Minute | 2 | 11-12 | `29` | minute 29 |
| Second | 2 | 13-14 | `02` | second 02 |
| Milliseconds (hex) | 2 | 15-16 | `40` | 64 (hundredths → 0.64s) |

Full time example: `112902.64` (11:29:02.64)

### IRQ/Receiver ID

The `01` and `0001` in positions 15-18 indicate:
- `01` = which receiver the tag was read on (01 = left-most receiver)
- `0001` = interrupt request ID (programmatic use)

---

## First-Seen / Last-Seen Format (Port 10200)

Same as raw format but with `FS` or `LS` appended, making it 38 characters:

```
aa000580017164f000010809271129024084FS
```

- `FS` = First-Seen: first time this tag was read in the current detection window
- `LS` = Last-Seen: last time this tag was read before leaving the detection zone

**Default timeout:** 5 seconds between FS and LS (configurable via Webmin).

### Recommendation

- **Start line:** Use `LS` (Last-Seen) — ensures the athlete has fully crossed the line
- **Finish / split lines:** Use `FS` (First-Seen) — captures the moment of first detection
- **Correction:** If a tag is read at the wrong timing point, it can be shifted manually

---

## Date-Time Records (Internal)

Records prefixed with `ab` report the reader's internal clock:

```
ab010a2c0811180212153062f102a9
```

| Field | Value | Meaning |
|-------|-------|---------|
| Prefix | `ab010a2c` | Date-time record type |
| Date | `081118` | November 18, 2008 (YYMMDD) |
| Day-of-week | `02` | Tuesday (2nd day) |
| Time | `12153062` | 12:15:30.98 (HHMMSS + hex ms) |
| Checksum | `f102a9` | LRC checksum |

---

## Connecting — Python Example

```python
import socket

HOST = "192.168.1.100"  # Reader IP address
PORT = 10200            # Use 10000 (raw), 10200 (FS/LS), or 10201 (XML)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))

while True:
    data = sock.recv(1024).decode('utf-8')
    for line in data.strip().split('\n'):
        if line.startswith('aa'):
            tag_id = line[2:14]
            print(f"Tag read: {tag_id}")
```

---

## LRC Checksum

The 6-character LRC (Longitudinal Redundancy Check) at the end of each record is calculated by the reader for data integrity verification. For most applications, records can be used without validating the LRC.

---

## Lite Reader Note

The IPICO Lite Reader uses the same IP-X protocol but communicates via a single TCP port (default often `10000`). The Lite Reader typically connects via wired Ethernet and uses the same tag ID format (12 chars, hex).

---

## Hardware Connection

- **Super Elite / Elite:** RJ45 Ethernet port for TCP/IP connection via UTP cable
- **Lite Reader:** Ethernet port; may use a specific IP address (check reader config)
- **Configuration:** Use the reader's built-in web interface (Webmin) or telnet to set the IP address
- **Power:** Internal battery or external 12V DC power supply

---

## References

- IPICO Sports Elite Reader User Manual v2.4 (December 2009)
- IPICO Sports Super Elite Reader User Manual v2.4 (June 2016)
