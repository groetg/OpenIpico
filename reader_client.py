#!/usr/bin/env python3
"""
OpenIpico — IPICO Sports RFID Reader Client

Connects to an IPICO timing reader via TCP/IP and parses tag data
in the IP-X protocol format.

Usage:
    python3 reader_client.py --host <reader-ip> [--port <port>]

Ports:
    10000 — Raw streaming (every tag read)
    10200 — First-Seen / Last-Seen (recommended for timing)
    10201 — XML format

Example:
    python3 reader_client.py --host 192.168.1.100 --port 10200
"""

import socket
import argparse
import sys
from datetime import datetime

BUFFER_SIZE = 4096


def parse_tag_record(raw: str) -> dict | None:
    """
    Parse a 36-character raw IPICO tag record.
    Format: aa<TAGID><DATETIME><IRQ><CHECKSUM>

    Returns a dict with parsed fields, or None if not a valid tag record.
    """
    line = raw.strip()
    if not line.startswith('aa') or len(line) < 36:
        return None

    # Raw format: aa<TAGID><DATETIME><IRQ><CHECKSUM>
    # But there may be FS/LS suffix
    is_fs_ls = line.endswith('FS') or line.endswith('LS')
    base = line[:36] if not is_fs_ls else line[:38]
    fs_ls = line[38:40] if is_fs_ls else None

    if len(base) < 36:
        return None

    tag_id = base[2:14]
    datetime_irq = base[14:30]
    checksum = base[30:36]

    # Parse datetime from the middle of the string
    # Format within datetime_irq (16 chars):
    # MM DD YY HH MM SS MS
    # But actual position is tricky — the manual shows:
    # The full string is: 00010809271129024084 (16 chars)
    # MM=08, DD=09, YY=27, HH=11, MM=29, SS=02, MS=40
    # "00" prefix might be IRQ part, let's check

    # The manual says: "aa000580017164f000010809271129024084"
    # After "aa" (2) and tag (12) = position 14
    # Then: "00010809271129024084"
    #   → 00 (irq/prefix)
    #   → 01 (receiver id: 01 or 02)
    #   → 08 (month)
    #   → 09 (day)
    #   → 27 (year)
    #   → 11 (hour)
    #   → 29 (minute)
    #   → 02 (second)
    #   → 40 (ms hundredths as hex)
    # That's 16 chars total

    irq = datetime_irq[:4]  # e.g. "0001"
    month = datetime_irq[4:6]
    day = datetime_irq[6:8]
    year = "20" + datetime_irq[8:10]
    hour = datetime_irq[10:12]
    minute = datetime_irq[12:14]
    second = datetime_irq[14:16]

    # ms is hex hundredths
    try:
        ms_hex = datetime_irq[16:18] if len(datetime_irq) > 16 else "00"
        ms = int(ms_hex, 16)
    except ValueError:
        ms = 0

    return {
        "raw": line,
        "tag_id": tag_id,
        "datetime": f"{year}-{month}-{day} {hour}:{minute}:{second}.{ms:02d}",
        "year": year,
        "month": month,
        "day": day,
        "hour": hour,
        "minute": minute,
        "second": second,
        "ms": ms,
        "irq": irq,
        "checksum": checksum,
        "fs_ls": fs_ls,  # 'FS', 'LS', or None
    }


def format_tag(record: dict) -> str:
    """Format a parsed tag record for display."""
    base = (f"[{record['datetime']}] "
            f"Tag: {record['tag_id']}")
    if record['fs_ls']:
        base += f" [{record['fs_ls']}]"
    return base


def connect(host: str, port: int):
    """Connect to the IPICO reader and stream tag data."""
    print(f"Connecting to {host}:{port}...")
    print("Press Ctrl+C to stop.\n")

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((host, port))
    except socket.error as e:
        print(f"ERROR: Could not connect to {host}:{port} — {e}", file=sys.stderr)
        sys.exit(1)

    print(f"✓ Connected. Receiving tag data (port {port}):\n")
    print("-" * 60)

    buffer = ""

    try:
        while True:
            data = sock.recv(BUFFER_SIZE).decode('utf-8', errors='replace')
            if not data:
                print("Connection closed by reader.")
                break

            buffer += data

            # Process complete lines
            while '\n' in buffer:
                line, buffer = buffer.split('\n', 1)
                line = line.strip()
                if not line:
                    continue

                # Parse and display
                record = parse_tag_record(line)
                if record:
                    print(format_tag(record))
                else:
                    # Other output (ab records, etc.)
                    if line.startswith('ab'):
                        print(f"[SYSTEM] {line}")
                    else:
                        print(f"[UNKNOWN] {line}")

    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        sock.close()


def main():
    parser = argparse.ArgumentParser(
        description="OpenIpico — Connect to IPICO timing readers"
    )
    parser.add_argument(
        '--host', '-H',
        required=True,
        help="IP address of the IPICO reader"
    )
    parser.add_argument(
        '--port', '-p',
        type=int,
        default=10200,
        help="TCP port (default: 10200 = FS/LS mode)"
    )
    args = parser.parse_args()

    connect(args.host, args.port)


if __name__ == '__main__':
    main()
