import os
from flask import Flask, render_template, jsonify, request
from datetime import date
import httpx
import csv_handler

app = Flask(__name__)

NTFY_TOPIC = "remembertada-hardeep"
CRON_SECRET = os.environ.get("CRON_SECRET", "dev-secret-change-in-production")


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


def verify_cron_secret():
    """Check the ?secret= query param matches CRON_SECRET."""
    return request.args.get("secret") == CRON_SECRET


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


@app.route("/api/remind-morning")
def remind_morning():
    """Cron-triggered endpoint for morning reminder (9:30 AM)."""
    if not verify_cron_secret():
        return jsonify({"error": "Unauthorized"}), 401
    result = run_reminder("morning")
    return jsonify(result)


@app.route("/api/remind-night")
def remind_night():
    """Cron-triggered endpoint for night reminder (9:30 PM)."""
    if not verify_cron_secret():
        return jsonify({"error": "Unauthorized"}), 401
    result = run_reminder("night")
    return jsonify(result)


@app.route("/api/ping")
def ping():
    """Health-check endpoint to keep the Render app alive."""
    return jsonify({"status": "ok", "time": str(date.today())})


if __name__ == "__main__":
    print("Remembertada starting...")
    print(f"   Phone notifications: https://ntfy.sh/{NTFY_TOPIC}")
    print("   Dashboard: http://localhost:5000")
    print()
    print("   Cron endpoints (protected by CRON_SECRET):")
    print("     GET /api/remind-morning?secret=...  (9:30 AM)")
    print("     GET /api/remind-night?secret=...   (9:30 PM)")
    print("     GET /api/ping                       (keep-alive)")
    app.run(debug=True, host="0.0.0.0", port=5000)
