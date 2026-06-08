import os
import httpx
import csv_handler

NTFY_TOPIC = "remembertada-hardeep"


def send_notification(title, message):
    """Send notification to phone via ntfy.sh."""
    try:
        r = httpx.post(
            f"https://ntfy.sh/{NTFY_TOPIC}",
            json={"topic": NTFY_TOPIC, "title": title, "message": message},
            timeout=10,
        )
        r.raise_for_status()
        print(f"[ntfy] Sent: {title} - {message}")
    except Exception as e:
        print(f"[Notification Error] {e}")


def run_reminder(timing):
    """Run reminder logic for given timing (morning/night)."""
    today_meds = csv_handler.get_todays_meds()
    filtered = [m for m in today_meds if m["timing"] == timing]
    pending = [m for m in filtered if not m["taken"]]

    timing_label = timing.capitalize()
    if pending:
        names = ", ".join(m["med_name"] for m in pending)
        send_notification(
            f"{timing_label} Medication",
            f"Time to take: {names}",
        )
        return {"status": "ok", "message": f"Reminder sent for {len(pending)} pending {timing} meds"}
    else:
        send_notification(
            f"{timing_label} Meds",
            f"All {timing} medications taken.",
        )
        return {"status": "ok", "message": f"No pending {timing} meds — all taken!"}
