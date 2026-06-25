import smtplib
from email.message import EmailMessage
import os
from crewai.tools import BaseTool

class SMTPEmailTool(BaseTool):
    name: str = "SMTP Email Sender Tool"
    description: str = "Sends an email with an optional attachment. If DRY_RUN is True, it only saves the email text locally and does not actually send."
    
    def _run(self, recipient_email: str, subject: str, body: str, attachment_filepath: str = None) -> str:
        dry_run = os.environ.get("DRY_RUN", "True").lower() == "true"
        
        # Hitl / Dry Run mode
        if dry_run:
            msg = f"--- [DRY RUN / HITL MODE] ---\n"
            msg += f"Would have sent email to: {recipient_email}\n"
            msg += f"Subject: {subject}\n\n"
            msg += f"Body:\n{body}\n\n"
            msg += f"Attachment Path: {attachment_filepath}\n"
            msg += f"------------------------------\n"
            
            # Save the intent to a local file for review
            output_dir = os.environ.get("OUTPUT_DIR", "output")
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, "email_dry_run.txt")
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(msg)
            
            return f"Dry run successful. Email content saved to {output_file} for manual review. Did not actually send to {recipient_email}."
        
        # Actual Sending mode
        sender_email = os.environ.get("SENDER_EMAIL")
        sender_password = os.environ.get("SENDER_APP_PASSWORD")
        smtp_server = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.environ.get("SMTP_PORT", 465))
        
        if not sender_email or not sender_password or sender_email == "your_email@gmail.com":
            return "Error: Valid SENDER_EMAIL or SENDER_APP_PASSWORD not set."
            
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg.set_content(body)
        
        if attachment_filepath and os.path.exists(attachment_filepath):
            with open(attachment_filepath, 'rb') as f:
                file_data = f.read()
                file_name = os.path.basename(attachment_filepath)
                msg.add_attachment(file_data, maintype='application', subtype='pdf', filename=file_name)
        else:
            if attachment_filepath:
                return f"Warning: Attachment {attachment_filepath} not found. Email aborted."
        
        try:
            with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
                server.login(sender_email, sender_password)
                server.send_message(msg)
            return f"Successfully sent email to {recipient_email}"
        except Exception as e:
            return f"Failed to send email. Error: {str(e)}"
