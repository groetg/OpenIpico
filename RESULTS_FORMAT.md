# Race Results Format (QuickExport CSV)

This document describes the race results export format used by OpenIpico, based on the `QuickExport.csv` format from iPicoWiz.

**Delimiter:** `;` (semicolon)

## Header

```csv
Pl;Bib;Name;Distance;Affiliation;Category;LapCount;LapCorrection;TotalDistance;AvgSpeed;GunTime;Result;FLap;Start;Run1-R1;Run1-R2;T1;Bike;T2;Finish
```

## Columns

| Column | Type | Description |
|--------|------|-------------|
| `Pl` | string/int | Final position/ranking. `DNS` = Did Not Start, `DNF` = Did Not Finish, `DSQ` = Disqualified |
| `Bib` | int | Athlete bib/start number |
| `Name` | string | Full athlete name |
| `Distance` | string | Race distance: `Normale afstand`, `Korte afstand`, `Jeugd (korte afstand)`, etc. |
| `Affiliation` | string | Club/team name |
| `Category` | string | Age/category: `M19-70` (men 19-70), `V19-70` (women 19-70), `Junioren`, `Jeugd (korte afstand)`, etc. |
| `LapCount` | int | Number of laps completed |
| `LapCorrection` | int | Manual lap corrections applied |
| `TotalDistance` | float | Total distance in km |
| `AvgSpeed` | float | Average speed in km/h |
| `GunTime` | time | Total time from gun start (HH:MM:SS) |
| `Result` | time | Net/final time (HH:MM:SS), subtracts gun-to-start delay |
| `FLap` | time | Final lap time |
| `Start` | time | Start time (HH:MM:SS) |
| `Run1-R1` | time | Run lap 1 (first running lap) |
| `Run1-R2` | time | Run lap 2 (second running lap, if applicable) |
| `T1` | time | Transition zone 1 time (swim→bike) |
| `Bike` | time | Bike segment time |
| `T2` | time | Transition zone 2 time (bike→run) |
| `Finish` | time | Finish run segment time |

## Time Format

All time fields use `HH:MM:SS` format (24-hour). Milliseconds are NOT stored in this export format.

Example: `00:56:11` = 56 minutes, 11 seconds.

For times that are not available or not applicable: empty or `-:--`.

## Status Markers

| Marker | Meaning |
|--------|---------|
| `DNS` | Did Not Start (registered but didn't start) |
| `DNF` | Did Not Finish (started but didn't complete) |
| `DSQ` | Disqualified |
| `-:--` | Not applicable / no data |

## Triathlon Segment Order

Based on the columns:

1. **Swim** → (implied before T1)
2. **T1** → Transition 1
3. **Bike** → Cycling segment
4. **T2** → Transition 2
5. **Run1-R1, Run1-R2** → Run laps (two lap sprint triathlon)
6. **Finish** → Final run segment

For sprint triathlon (Normale/Korte afstand):
- LapCount typically 7
- Swim + Bike + Run segments combined

## Example Row

```
1;53;Michael Emmerik;Normale afstand;DTC Heerhugowaard;M19-70;7;0;0;0;00:56:42;00:56:11;00:00:34;00:00:31;00:07:32;00:07:31;00:00:41;00:32:32;00:00:34;00:07:23
```

Interpretation:
- Position 1, Bib 53, Michael Emmerik, DTC Heerhugowaard
- Category: Men 19-70, Sprint triathlon (7 laps)
- Gun time: 56:42, Net time: 56:11
- Swim start: 00:00:31
- T1: 00:07:32, Bike: 00:32:32, T2: 00:00:34, Finish: 00:07:23
- First lap (FLap): 00:00:34

## DNS/DNF Examples

```
DNS;10;Corrina Leeflang;Normale afstand;Zwefilo;V19-70;0;0;0;;DNS;DNS;DNS;;;;;;;
```

- Position = DNS
- Bib = 10
- All timing fields are empty or DNS
- LapCount = 0 (didn't start any lap)

## Lap Correction

`LapCorrection` tracks how many times a passing was manually shifted/adjusted by the operator — this is exactly the feature that Guido needs in OpenIpico that iPicoWiz lacks.

Format: integer count of corrections applied.
