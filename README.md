# Remembertada

A personal medication reminder dashboard that sends push notifications to your phone at 9:30 AM and 9:30 PM via [ntfy.sh](https://ntfy.sh).

## Quick Start (Local)

```bash
pip install -r requirements.txt
python3 app.py
```

Then open http://localhost:5000

## Architecture

- **Flask web app** — dashboard + JSON API, hosted on PythonAnywhere
- **ntfy.sh** — push notifications to your phone
- **cron-job.org** — free external cron service triggers reminders at 9:30 AM/PM
- **CSV file** — medication schedule data

No APScheduler or server-side scheduler needed — cron-job.org handles the timing externally.

## Deployment (PythonAnywhere)

### Step 1: Push to GitHub

```bash
git push origin master
```

### Step 2: Open PythonAnywhere

1. Go to [pythonanywhere.com](https://www.pythonanywhere.com) and create a **Free** account (no card needed)
2. Open a **Bash console** from the Dashboard

### Step 3: Clone the repo

```bash
git clone https://github.com/Dashetty/RememeberTada.git
cd RememeberTada
```

### Step 4: Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 5: Set up the web app

1. Go to the **Web** tab → **Add a new web app**
2. Choose **Manual Configuration** → **Python 3.12**
3. Set the source code directory to `/home/Dashetty/RememeberTada`
4. Set the virtualenv to `/home/Dashetty/RememeberTada/venv`

### Step 6: Configure WSGI file

Open the WSGI file at `/var/www/dashetty_pythonanywhere_com_wsgi.py` and replace everything with:

```python
import sys
import os

path = '/home/Dashetty/RememeberTada'
if path not in sys.path:
    sys.path.append(path)

os.environ['CSV_PATH'] = '/home/Dashetty/RememeberTada/medication_schedule.csv'
os.environ['CRON_SECRET'] = 'your-secret-key-here-change-this'

from app import app as application
```

### Step 7: Reload

Click the **Reload** button on the Web tab.

### Step 8: Set up cron-job.org (free, no card needed)

Go to [cron-job.org](https://cron-job.org) and create a **free account**. Then create **3 jobs**:

| # | URL | Schedule | Description |
|---|---|---|---|
| 1 | `https://Dashetty.pythonanywhere.com/api/remind-morning?secret=YOUR_CRON_SECRET` | `30 9 * * *` (9:30 AM daily) | Morning reminder |
| 2 | `https://Dashetty.pythonanywhere.com/api/remind-night?secret=YOUR_CRON_SECRET` | `30 21 * * *` (9:30 PM daily) | Night reminder |
| 3 | `https://Dashetty.pythonanywhere.com/api/ping` | Every 10 minutes | Keep-alive |

Replace `YOUR_CRON_SECRET` with the same secret you put in the WSGI file.

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
- ntfy.sh (push notifications)
- PythonAnywhere (hosting)
- cron-job.org (free cron scheduling)
- Minimalist UI (warm monochrome + editorial typography)
