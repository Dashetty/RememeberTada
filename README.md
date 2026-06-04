# Remembertada

A personal medication reminder dashboard. Reads your CSV schedule and sends system notifications at 9:30 AM and 9:30 PM.

## Setup

```bash
pip install -r requirements.txt
python3 app.py
```

Then open http://localhost:5000

## CSV Format

```
Date,MedName,Timings,Taken
29/05/2026,Mincaffin oral,morning,taken
,TufHair Tablets,Night,taken
```

- Empty date cells inherit from the row above
- `Taken` column: `taken` or blank

## Tech Stack

- Python 3 + Flask
- APScheduler (9:30 AM / 9:30 PM reminders)
- plyer (system desktop notifications)
- Minimalist UI (warm monochrome + editorial typography)
