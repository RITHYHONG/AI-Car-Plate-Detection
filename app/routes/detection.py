from flask import jsonify, request, render_template, current_app, redirect, url_for, flash
from app.routes import detection_bp
from app.database.models import Detection, Ticket, db
from app.utils.preprocess import save_uploaded_file
from app.utils.ticket import generate_ticket
from app.training import DataCollector  # Updated import
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from app.models import get_detector, get_ocr_model
import cv2
import uuid

@detection_bp.route('/')
def index():
    return render_template('index.html')

@detection_bp.route('/logs')
def logs():
    detections = Detection.query.order_by(Detection.timestamp.desc()).all()
    return render_template('logs.html', detections=detections)

@detection_bp.route('/api/detections', methods=['GET'])
def get_detections():
    with current_app.app_context():
        detections = Detection.query.order_by(Detection.timestamp.desc()).limit(10).all()
        return jsonify([detection.to_dict() for detection in detections])

@detection_bp.route('/api/detection/<ticket_id>')
def get_detection(ticket_id):
    detection = Detection.query.filter_by(ticket_id=ticket_id).first_or_404()
    return jsonify(detection.to_dict())

@detection_bp.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
        
    try:
        # Save and process the uploaded file
        filepath = save_uploaded_file(file)
        
        # Generate ticket
        ticket_id = generate_ticket(filepath)
        
        return jsonify({
            'message': 'File uploaded successfully',
            'ticket_id': ticket_id
        })
        
    except Exception as e:
        current_app.logger.error(f"Upload error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@detection_bp.route('/api/tickets/<ticket_id>/print', methods=['POST'])
def print_ticket(ticket_id):
    ticket = Ticket.query.filter_by(ticket_id=ticket_id).first_or_404()
    
    try:
        # Update ticket status
        ticket.printed = True
        ticket.printed_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Ticket printed successfully',
            'ticket': ticket.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Print error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@detection_bp.route('/upload_image', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('detection.index'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('detection.index'))
    
    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            detector = get_detector()
            ocr_model = get_ocr_model()
            
            image = cv2.imread(file_path)
            if image is None:
                flash('Error reading image file')
                return redirect(url_for('detection.index'))
                
            detections = detector.detect(image)
            results = []
            
            # Create data collector instance
            data_collector = DataCollector()
            
            for detection in detections:
                x, y, w, h = detection['box']
                cropped_image = image[y:y+h, x:x+w]
                plate_number = ocr_model.read_text(cropped_image)
                
                if plate_number:
                    # Save training sample
                    data_collector.save_training_sample(
                        cropped_image,
                        plate_number,
                        (x, y, w, h),
                        detection['confidence']
                    )
                    
                    ticket_id = str(uuid.uuid4())
                    detection_record = Detection(
                        plate_number=plate_number,
                        confidence=detection['confidence'],
                        image_path=file_path,
                        ticket_id=ticket_id,
                        timestamp=datetime.utcnow()
                    )
                    db.session.add(detection_record)
                    db.session.commit()
                    
                    results.append({
                        'plate_number': plate_number,
                        'confidence': round(detection['confidence'] * 100, 2),
                        'status': 'Detected'
                    })
            
            if not results:
                flash('No license plates detected in the image')
            
            return render_template('index.html', results=results)
            
        except Exception as e:
            current_app.logger.error(f"Detection error: {str(e)}")
            db.session.rollback()
            flash(f'An error occurred during detection: {str(e)}')
            return redirect(url_for('detection.index'))
    
    flash('Invalid file type')
    return redirect(url_for('detection.index'))

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']