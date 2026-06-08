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
- **PythonAnywhere Tasks** — built-in cron scheduler triggers reminders at 9:30 AM/PM
- **CSV file** — medication schedule data

No APScheduler needed — PythonAnywhere runs the reminder scripts directly via its Tasks tab.

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
4. Set the WSGI configuration file to point to the Flask app (PythonAnywhere's auto-generated WSGI file will need updating — guide below)

### Step 6: Configure WSGI file

In the Web tab, click on the WSGI configuration file link. Replace its contents with:

```python
import sys
path = '/home/Dashetty/RememeberTada'
if path not in sys.path:
    sys.path.append(path)

from app import app as application
```

### Step 7: Set environment variables

In the Web tab, go to the **Environment variables** section and add:

| Key | Value |
|---|---|
| `CSV_PATH` | `/home/Dashetty/RememeberTada/medication_schedule.csv` |

### Step 8: Reload and test

Click the green **Reload** button. Visit `https://Dashetty.pythonanywhere.com/` to see your dashboard.

### Step 9: Set up scheduled tasks

Go to the **Tasks** tab and add two daily tasks:

| Time | Command |
|---|---|
| `09:30` | `cd /home/Dashetty/RememeberTada && source venv/bin/activate && python run_task.py morning` |
| `21:30` | `cd /home/Dashetty/RememeberTada && source venv/bin/activate && python run_task.py night` |

That's it — you'll get notifications on your phone at 9:30 AM and 9:30 PM every day.

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
- PythonAnywhere (hosting + scheduled tasks)
- Minimalist UI (warm monochrome + editorial typography)
