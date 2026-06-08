# Remembertada

A personal medication reminder dashboard that sends push notifications to your phone at 9:30 AM and 9:30 PM via [ntfy.sh](https://ntfy.sh).

## Quick Start (Local)

```bash
pip install -r requirements.txt
python3 app.py
```

Then open http://localhost:5000

## Architecture

- **Flask web app** — dashboard + JSON API
- **ntfy.sh** — push notifications to phone
- **cron-job.org** (or Render Cron) — triggers reminder endpoints at 9:30 AM/PM
- **CSV file** — medication schedule data

### Why not APScheduler?

Free hosting platforms (Render, Railway, etc.) spin down apps during inactivity, which kills in-process schedulers. Instead, an external cron service pings two API endpoints:

| Endpoint | Schedule | What it does |
|---|---|---|
| `GET /api/remind-morning?secret=...` | 9:30 AM daily | Sends morning medication reminder |
| `GET /api/remind-night?secret=...` | 9:30 PM daily | Sends night medication reminder |
| `GET /api/ping` | Every 10 min | Keeps the Render app alive |

All cron endpoints (except `/api/ping`) are protected by `CRON_SECRET`.

## Deployment (Render)

### One-click deploy

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/Dashetty/RememeberTada)

The `render.yaml` is pre-configured with:
- Python 3.12 runtime
- 2 gunicorn workers
- Auto-generated `CRON_SECRET`
- Cron jobs for morning (9:30 AM) and night (9:30 PM) reminders

### Manual deploy

1. Push this repo to GitHub
2. On [Render Dashboard](https://dashboard.render.com) → New Web Service
3. Connect your repo
4. Set these environment variables:

| Variable | Value |
|---|---|
| `PYTHON_VERSION` | `3.12` |
| `CRON_SECRET` | (generate a random string) |
| `CSV_PATH` | `medication_schedule.csv` (default) |

5. Deploy — Render automatically detects the `Procfile`

### Set up cron jobs (if not using render.yaml)

Create two cron jobs on [cron-job.org](https://cron-job.org) (free):

| URL | Schedule |
|---|---|
| `https://your-app.onrender.com/api/remind-morning?secret=YOUR_SECRET` | Every day at 9:30 AM |
| `https://your-app.onrender.com/api/remind-night?secret=YOUR_SECRET` | Every day at 9:30 PM |

Also create a keep-alive ping every 10 minutes to `https://your-app.onrender.com/api/ping`.

## CSV Format

```
Date,MedName,Timings,Taken
29/05/2026,Mincaffin oral,morning,taken
,TufHair Tablets,Night,taken
```

- Empty date cells inherit from the row above
- `Taken` column: `taken` or blank

## Tech Stack

- Python 3 + Flask + Gunicorn
- ntfy.sh (push notifications)
- cron-job.org or Render Cron (scheduling)
- Minimalist UI (warm monochrome + editorial typography)
