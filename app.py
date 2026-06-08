import os
from flask import Flask, render_template, jsonify, request
from datetime import date
import csv_handler
import reminder

app = Flask(__name__)

CRON_SECRET = os.environ.get("CRON_SECRET", "dev-secret-change-in-production")


def verify_cron_secret():
    """Check the ?secret= query param matches CRON_SECRET."""
    return request.args.get("secret") == CRON_SECRET


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
    result = reminder.run_reminder("morning")
    return jsonify(result)


@app.route("/api/remind-night")
def remind_night():
    """Cron-triggered endpoint for night reminder (9:30 PM)."""
    if not verify_cron_secret():
        return jsonify({"error": "Unauthorized"}), 401
    result = reminder.run_reminder("night")
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
