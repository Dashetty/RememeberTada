from flask import Flask, render_template, jsonify, request
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from plyer import notification
from datetime import date
import csv_handler

app = Flask(__name__)
scheduler = BackgroundScheduler()
scheduler.start()


def send_notification(title, message):
    """Send a system-wide desktop notification."""
    try:
        notification.notify(
            title=title,
            message=message,
            timeout=15,
        )
    except Exception as e:
        print(f"[Notification Error] {e}")


def morning_reminder():
    """9:30 AM reminder — check for morning meds."""
    today_meds = csv_handler.get_todays_meds()
    morning_meds = [m for m in today_meds if m["timing"] == "morning"]
    pending = [m for m in morning_meds if not m["taken"]]

    if pending:
        names = ", ".join(m["med_name"] for m in pending)
        send_notification(
            "💊 Morning Medication Reminder",
            f"Time to take: {names}",
        )
    else:
        send_notification(
            "💊 Morning Meds",
            "All morning medications taken! ✅",
        )


def night_reminder():
    """9:30 PM reminder — check for night meds."""
    today_meds = csv_handler.get_todays_meds()
    night_meds = [m for m in today_meds if m["timing"] == "night"]
    pending = [m for m in night_meds if not m["taken"]]

    if pending:
        names = ", ".join(m["med_name"] for m in pending)
        send_notification(
            "💊 Night Medication Reminder",
            f"Time to take: {names}",
        )
    else:
        send_notification(
            "💊 Night Meds",
            "All night medications taken! ✅",
        )


# Schedule reminders
scheduler.add_job(
    morning_reminder,
    CronTrigger(hour=9, minute=30),
    id="morning_reminder",
    replace_existing=True,
)
scheduler.add_job(
    night_reminder,
    CronTrigger(hour=21, minute=30),
    id="night_reminder",
    replace_existing=True,
)


@app.route("/")
def dashboard():
    """Main dashboard showing today's and upcoming meds."""
    today_meds = csv_handler.get_todays_meds()
    upcoming = csv_handler.get_upcoming_meds(days=7)

    # Group upcoming by date
    upcoming_by_date = {}
    for m in upcoming:
        d = m["date"].isoformat()
        if d not in upcoming_by_date:
            upcoming_by_date[d] = []
        upcoming_by_date[d].append(m)

    return render_template(
        "dashboard.html",
        today_meds=today_meds,
        upcoming_by_date=upcoming_by_date,
        today=date.today(),
    )


@app.route("/api/mark-taken", methods=["POST"])
def mark_taken():
    """API endpoint to mark a medication as taken."""
    data = request.json
    med_name = data.get("med_name")
    timing = data.get("timing")

    if not med_name or not timing:
        return jsonify({"error": "Missing med_name or timing"}), 400

    success = csv_handler.mark_taken(med_name, timing)
    if success:
        return jsonify({"status": "ok", "message": f"Marked {med_name} as taken"})
    else:
        return jsonify({"status": "error", "message": "Med not found in CSV"}), 404


@app.route("/api/meds")
def api_meds():
    """JSON API for today's meds (for auto-refresh)."""
    meds = csv_handler.get_todays_meds()
    return jsonify(meds)


if __name__ == "__main__":
    print("🏥 Remembertada starting...")
    print("   Dashboard: http://localhost:5000")
    print("   Morning reminder: 9:30 AM")
    print("   Night reminder: 9:30 PM")
    app.run(debug=True, host="0.0.0.0", port=5000)
