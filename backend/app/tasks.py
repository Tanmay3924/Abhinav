from app import celery
from flask_mail import Message
from . import mail, db
from .models import User, Reservation, get_ist_time
import csv
import io
from datetime import timedelta

@celery.task(name="export_reservations_csv")
def export_reservations_csv(admin_email):
    print(f"Starting CSV Export for {admin_email}...")

    reservations = Reservation.query.order_by(Reservation.parked_at.desc()).all()

    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['ID', 'User ID', 'Spot ID', 'Parked At', 'Left At', 'Cost', 'Remarks'])

    for r in reservations:
        cw.writerow([
            r.id, r.user_id, r.spot_id,
            r.parked_at, r.left_at, r.cost, r.remarks
        ])

    output = si.getvalue()

    try:
        msg = Message("Parking Reservations Export", recipients=[admin_email])
        msg.body = "Please find the attached CSV report."
        msg.attach("reservations.csv", "text/csv", output)
        mail.send(msg)
        return "Email Sent Successfully"
    except Exception as e:
        print(f"Error sending email: {e}")
        return f"Failed: {str(e)}"
