import csv
import os
from datetime import datetime, date

CSV_PATH = "/mnt/windrive/Zorin-Share/Downloads/Misc/60-Day Medication Schedule Final.csv"


def parse_csv():
    """Parse CSV and return list of med entries with resolved dates."""
    entries = []
    last_date = None

    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Handle inherited dates (empty date cell = same date as previous row)
            raw_date = row.get("Date", "").strip()
            if raw_date:
                last_date = datetime.strptime(raw_date, "%d/%m/%Y").date()

            if last_date is None:
                continue

            entries.append({
                "date": last_date,
                "date_str": last_date.strftime("%d/%m/%Y"),
                "med_name": row.get("MedName", "").strip(),
                "timing": row.get("Timings", "").strip().lower(),
                "taken": row.get("Taken", "").strip().lower() == "taken",
            })

    return entries


def get_todays_meds():
    """Get today's medications."""
    today = date.today()
    all_entries = parse_csv()
    return [e for e in all_entries if e["date"] == today]


def get_upcoming_meds(days=7):
    """Get medications for the next N days."""
    today = date.today()
    from datetime import timedelta
    end = today + timedelta(days=days)
    all_entries = parse_csv()
    return [e for e in all_entries if today <= e["date"] <= end]


def mark_taken(med_name, timing):
    """Mark a medication as taken for today in the CSV."""
    today = date.today()
    rows = []
    updated = False

    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows.append(header)

        last_date = None
        for row in reader:
            raw_date = row[0].strip() if len(row) > 0 else ""
            if raw_date:
                try:
                    last_date = datetime.strptime(raw_date, "%d/%m/%Y").date()
                except ValueError:
                    pass

            # Match by date + med_name + timing
            if (last_date == today
                    and len(row) > 1
                    and row[1].strip() == med_name
                    and len(row) > 2
                    and row[2].strip().lower() == timing.lower()):
                row[3] = "taken"
                updated = True

            rows.append(row)

    if updated:
        with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(rows)

    return updated


def is_med_scheduled_today(entry):
    """Check if a med entry is actually scheduled for its date (handles every-other-day)."""
    return True  # CSV already encodes the schedule, so all entries are valid


if __name__ == "__main__":
    print("=== Today's Meds ===")
    for m in get_todays_meds():
        status = "✅ Taken" if m["taken"] else "⏳ Pending"
        print(f"  {m['med_name']} ({m['timing']}) - {status}")

    print("\n=== Upcoming 7 Days ===")
    for m in get_upcoming_meds(7):
        status = "✅" if m["taken"] else "⏳"
        print(f"  {m['date_str']} | {m['med_name']} ({m['timing']}) {status}")
