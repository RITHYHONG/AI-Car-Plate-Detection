from datetime import datetime
import os
from flask import current_app
from app.database.models import Ticket, db
import uuid
from PIL import Image, ImageDraw, ImageFont
import qrcode

def generate_ticket(plate_number):
    """
    Generate a unique ticket ID and create ticket entry
    """
    timestamp = datetime.utcnow()
    ticket_id = f"TICKET_{timestamp.strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:6]}"
    
    # Create ticket image
    ticket_path = create_ticket_image(ticket_id, plate_number, timestamp)
    
    # Create ticket record
    ticket = Ticket(
        ticket_id=ticket_id,
        generated_at=timestamp,
        image_path=ticket_path,
        plate_number=plate_number  # Add plate number to the ticket record
    )
    
    db.session.add(ticket)
    db.session.commit()
    
    return ticket_id

def create_ticket_image(ticket_id, plate_number, timestamp):
    """
    Create a visual ticket as an image
    """
    # Create a new image with white background
    width = 600
    height = 400
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    try:
        # Load font (use a default font if custom font not available)
        font_path = os.path.join(current_app.static_folder, 'fonts', 'Arial.ttf')
        font = ImageFont.truetype(font_path, 32)
    except:
        font = ImageFont.load_default()
    
    # Add ticket information
    draw.text((50, 50), "Parking Ticket", font=font, fill='black')
    draw.text((50, 100), f"Plate Number: {plate_number}", font=font, fill='black')
    draw.text((50, 150), f"Date: {timestamp.strftime('%Y-%m-%d')}", font=font, fill='black')
    draw.text((50, 200), f"Time: {timestamp.strftime('%H:%M:%S')}", font=font, fill='black')
    draw.text((50, 250), f"Ticket ID: {ticket_id}", font=font, fill='black')
    
    # Generate and add QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=5,
        border=4,
    )
    qr.add_data(ticket_id)
    qr.make(fit=True)
    qr_image = qr.make_image(fill_color="black", back_color="white")
    
    # Paste QR code onto ticket
    image.paste(qr_image, (400, 50))
    
    # Save ticket image
    ticket_path = os.path.join(current_app.config['UPLOAD_FOLDER'], f'ticket_{ticket_id}.png')
    image.save(ticket_path)
    
    return ticket_path

def get_ticket_path(ticket_id):
    """
    Get the file path for a ticket image
    """
    return os.path.join(current_app.config['UPLOAD_FOLDER'], f'ticket_{ticket_id}.png')

def delete_ticket(ticket_id):
    """
    Delete a ticket and its associated image
    """
    ticket = Ticket.query.filter_by(ticket_id=ticket_id).first()
    if ticket:
        # Delete ticket image if it exists
        if ticket.image_path and os.path.exists(ticket.image_path):
            os.remove(ticket.image_path)
            
        # Delete database record
        db.session.delete(ticket)
        db.session.commit()
        return True
    return False