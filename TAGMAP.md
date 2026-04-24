# TagMap — Bib-to-Chip Mapping

Each race/event requires a **TagMap** that maps RFID tag IDs to athlete bib numbers (startnummers).

## Format

Simple CSV with header `Num,Tag`:

```csv
Num,Tag
1,0580a01f5271
2,0580a01f4ce0
3,0580a01f618c
...
```

| Field | Description |
|-------|-------------|
| `Num` | Bib / start number (race number) |
| `Tag` | 12-character hexadecimal RFID tag ID |

## Tag ID Format

All IPICO tags start with `058` followed by 9 hex characters:

```
0580a01f5271
^^^-----------
Tag ID prefix
```

Tags from the same production batch share a prefix (e.g., `0580a01f...`, `058000a...`, `0580a05f...`).

## TagMap Storage

TagMaps are stored per-event in the `/events/{event_id}/tagmap.csv`.

Example path: `/events/2024-001-triathlon-zwem/TAGMAP.csv`

## Usage

When a tag pass is received:

```python
# Load tagmap
tagmap = {}
with open("tagmap.csv") as f:
    next(f)  # skip header
    for line in f:
        num, tag = line.strip().split(",")
        tagmap[tag] = int(num)

# Resolve a tag read
tag_id = "0580a01f5271"
bib = tagmap.get(tag_id)  # → 1
```

## Source

TagMaps are provided by the race organizer and are event-specific. They link the physical RFID tags (attached to shoes or race numbers) with the athlete registration data (name, club, category, etc.).

**Note:** The TagMap format used here is based on the `TagMap2024_v3.txt` provided by Guido Groet. Other timing systems may use different formats (e.g., separate `chipcode` and `biba` columns, or different delimiters).
