from ISPROJECT import settings
import africastalking
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch

import random
import string

def generate_random_string(length, prefix=''):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    random_string = random_string.upper()
    if prefix != "":
        random_string = f'{prefix}-{random_string}'

    return random_string


def send_sms(phone, message):
    # Code to send sms
    africastalking.initialize(username=settings.AFRICASTALKING_USERNAME, api_key=settings.AFRICASTALKING_API_KEY)
    africastalking.SMS.send(message, ['+254799773244'])



def create_certificate(client_name, course_name, date_of_issue, expiry_date, firearm_type, license_no):
    c = canvas.Canvas(f"{client_name}_licence.pdf", pagesize=letter)
    width, height = letter

    # Draw the border
    c.setLineWidth(4)
    c.setStrokeColor(colors.black)
    c.rect(0.5 * inch, 0.5 * inch, width - inch, height - inch, stroke=1, fill=0)

    # licence Number 
    c.setFont("Helvetica", 16)
    c.drawCentredString(width / 2.0, height - 1.5 * inch, f"Licence Number: {license_no}")

    # Title
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width / 2.0, height - 2.5 * inch, "Firearms License Certificate")


    # Subtitle
    c.setFont("Helvetica", 18)
    c.drawCentredString(width / 2.0, height - 3.5 * inch, f"This certifies that")

    # Client name
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(width / 2.0, height - 4.5 * inch, client_name)

    # Course name
    c.setFont("Helvetica", 18)
    c.drawCentredString(width / 2.0, height - 5.5 * inch, f"is licenced to own a lincensed {firearm_type} firearm.")

    # Course details
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width / 2.0, height - 6.5 * inch, course_name)

    # Completion date
    c.setFont("Helvetica", 16)
    c.drawCentredString(width / 2.0, height - 7.5 * inch, f"Date of Issue: {date_of_issue} \nDate of Expiry: {expiry_date}")
    

    # # Add image
    # if image_path:
    #     c.drawImage(image_path, width / 2.0 - 1 * inch, height - 8 * inch, width=2 * inch, height=2 * inch)

    # Save the PDF file
    c.save()

    return c.getpdfdata()

# Example usage
