class Observer:
    """Base Observer interface."""
    def update(self, subject):
        raise NotImplementedError("Subclasses must implement `update` method.")

class Subject:
    """Base Subject for managing observers."""
    def __init__(self):
        self._observers = []

    def add_observer(self, observer):
        """Add an observer to the list."""
        self._observers.append(observer)

    def remove_observer(self, observer):
        """Remove an observer from the list."""
        self._observers.remove(observer)

    def notify_observers(self):
        """Notify all observers of a state change."""
        for observer in self._observers:
            observer.update(self)

class AlertObserver(Observer):
    """Observer for sending budget alerts."""
    def update(self, subject):
        print(f"[DEBUG] Observer Notified: Limit={subject.limit}, Current Total={subject.current_total}, Alert Sent={subject.alert_sent}")

        # Skip alert if no budget limit or already sent
        if subject.limit == 0 or subject.alert_sent:
            return

        if subject.current_total > subject.limit and not subject.alert_sent:
            excess_amount = subject.current_total - subject.limit
            self.send_alert(excess_amount)
            subject.alert_sent = True

    def send_alert(self, excess_amount):
        """Send an alert email."""
        from flask_mail import Message
        from flask_login import current_user
        from app.extensions import mail
        from flask import current_app

        with current_app.app_context():  
            msg = Message(
                "Budget Exceeded Alert!",
                sender="YousifZito4SA3@gmail.com",
                recipients=[current_user.email],
            )
            msg.body = f"Hello {current_user.username},\n\nYou have exceeded your budget by ${excess_amount:.2f}.\n\nThank you!"
            # mail.send(msg)

class LoggingObserver(Observer):
    """Observer for logging budget changes."""
    def update(self, subject):
        if subject.limit == 0:
            print("[LOG] Budget deleted: Limit=0, Current Total=0")
        else:
            print(f"[LOG] Budget updated: Limit={subject.limit}, Current Total={subject.current_total}")

class SMSObserver(Observer):
    """Observer for sending SMS budget alerts."""
    
    def update(self, subject):
        """Send an SMS alert when the budget is exceeded."""
        if subject.limit == 0:
            return
        
        if subject.current_total > subject.limit:
            excess_amount = subject.current_total - subject.limit
            self.send_sms(excess_amount)
            subject.alert_sent = True

    def send_sms(self, excess_amount):
        """Simulate sending an SMS."""
        print(f"[SMS ALERT] You have exceeded your budget by ${excess_amount:.2f}!")

class DashboardObserver(Observer):
    """Observer for updating the UI dashboard."""
    
    def update(self, subject):
        """Update the frontend dashboard with the latest budget data."""
        print(f"[DASHBOARD] Updating UI: Limit={subject.limit}, Current Total={subject.current_total}")
        self.update_ui(subject.limit, subject.current_total)

    def update_ui(self, limit, total):
        """Simulate sending data to the frontend dashboard."""
        print(f"[DASHBOARD] Updated: New Limit = {limit}, Current Spending = {total}")