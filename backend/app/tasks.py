from app import celery
from flask_mail import Message
from . import mail, db
from .models import User, Reservation, ParkingSpot, ParkingLot
import csv
import io
from datetime import datetime, timedelta
from sqlalchemy import func

# --- Existing CSV Export Task ---
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

# --- NEW: Daily Reminders ---
@celery.task(name="daily_reminders")
def daily_reminders():
    """
    Sends an email to users who currently have an ACTIVE reservation (haven't left yet).
    """
    print("Running Daily Reminders...")
    
    # Find active reservations (left_at is None)
    active_reservations = Reservation.query.filter_by(left_at=None).all()
    
    count = 0
    for res in active_reservations:
        user = User.query.get(res.user_id)
        spot = ParkingSpot.query.get(res.spot_id)
        lot = ParkingLot.query.get(spot.lot_id)
        
        if user and user.email:
            subject = "🚗 ParkZone Reminder: You have an active parking spot"
            html_body = f"""
            <h3>Hi {user.username},</h3>
            <p>This is a reminder that you have an active parking session.</p>
            <ul>
                <li><strong>Location:</strong> {lot.prime_location_name}</li>
                <li><strong>Spot Number:</strong> {spot.spot_number}</li>
                <li><strong>Parked Since:</strong> {res.parked_at.strftime('%d-%m-%Y %I:%M %p')}</li>
            </ul>
            <p>Don't forget to release your spot when you leave!</p>
            <br>
            <p>Regards,<br>Team ParkZone</p>
            """
            
            try:
                msg = Message(subject, recipients=[user.email], html=html_body)
                mail.send(msg)
                count += 1
            except Exception as e:
                print(f"Failed to send reminder to {user.email}: {e}")

    return f"Sent {count} daily reminders."

# --- NEW: Monthly Activity Report ---
@celery.task(name="monthly_activity_report")
def monthly_activity_report():
    """
    Sends a monthly summary PDF/HTML to all users about their usage in the previous month.
    """
    print("Running Monthly Reports...")
    
    # Calculate dates for "Last Month"
    today = datetime.now()
    first_day_this_month = today.replace(day=1)
    last_day_prev_month = first_day_this_month - timedelta(days=1)
    first_day_prev_month = last_day_prev_month.replace(day=1)
    # first_day_prev_month = first_day_this_month
    # last_day_prev_month = today
    # Format for display (e.g., "November 2025")
    month_name = first_day_prev_month.strftime("%B %Y")
    
    users = User.query.all()
    sent_count = 0
    
    for user in users:
        # Get stats for this user for the previous month
        # We look for reservations that 'left_at' in the previous month
        reservations = Reservation.query.filter(
            Reservation.user_id == user.id,
            Reservation.left_at >= first_day_prev_month,
            Reservation.left_at <= last_day_prev_month
        ).all()
        
        if not reservations:
            continue # Skip users with no activity
            
        total_spent = sum(r.cost for r in reservations if r.cost)
        total_visits = len(reservations)
        
        subject = f"📊 Your ParkZone Report - {month_name}"
        
        # Simple HTML Template
        html_body = f"""
        <div style="font-family: Arial, sans-serif; padding: 20px; border: 1px solid #ddd;">
            <h2 style="color: #4f46e5;">ParkZone Monthly Report</h2>
            <p>Hi <strong>{user.username}</strong>,</p>
            <p>Here is your parking summary for <strong>{month_name}</strong>.</p>
            
            <table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
                <tr style="background-color: #f8f9fa;">
                    <th style="padding: 10px; border: 1px solid #ddd;">Total Visits</th>
                    <th style="padding: 10px; border: 1px solid #ddd;">Total Spent</th>
                </tr>
                <tr>
                    <td style="padding: 10px; border: 1px solid #ddd; text-align: center;">{total_visits}</td>
                    <td style="padding: 10px; border: 1px solid #ddd; text-align: center;">₹{total_spent:.2f}</td>
                </tr>
            </table>
            
            <p style="margin-top: 20px;">Visit your dashboard for more details.</p>
            <p>Keep Parking Smart!</p>
        </div>
        """
        
        try:
            msg = Message(subject, recipients=[user.email], html=html_body)
            mail.send(msg)
            sent_count += 1
        except Exception as e:
            print(f"Failed to send report to {user.email}: {e}")

    return f"Sent {sent_count} monthly reports."