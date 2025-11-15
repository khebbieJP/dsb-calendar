#!/usr/bin/env python3
"""
Flask web application for DSB ticket PDF to ICS conversion
"""

import os
import tempfile
from pathlib import Path
from flask import Flask, request, jsonify, send_file, render_template
from werkzeug.utils import secure_filename

from dsb_converter.api import extract_ticket_info, create_ics_bytes
from dsb_converter.api.parsers import TicketParsingError
from dsb_converter.api.calendar import CalendarGenerationError


app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

ALLOWED_EXTENSIONS = {'pdf'}


def allowed_file(filename):
    """Check if file has an allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'DSB Ticket to ICS Converter',
        'version': '1.0.0'
    })


@app.route('/api/convert', methods=['POST'])
def convert_pdf():
    """
    Convert a DSB ticket PDF to ICS format.

    Accepts a PDF file upload and returns either:
    - JSON with ticket information (if format=json)
    - ICS file download (if format=ics or not specified)
    """
    # Validate request
    if 'file' not in request.files:
        return jsonify({
            'error': 'No file provided',
            'message': 'Please upload a PDF file'
        }), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({
            'error': 'No file selected',
            'message': 'Please select a file to upload'
        }), 400

    if not allowed_file(file.filename):
        return jsonify({
            'error': 'Invalid file type',
            'message': 'Only PDF files are allowed'
        }), 400

    # Get response format preference
    response_format = request.form.get('format', 'ics').lower()

    try:
        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        temp_pdf = Path(app.config['UPLOAD_FOLDER']) / filename
        file.save(temp_pdf)

        try:
            # Extract ticket information
            info = extract_ticket_info(temp_pdf)

            if not info.is_valid():
                return jsonify({
                    'error': 'Incomplete ticket information',
                    'message': 'Could not extract all required information from the PDF',
                    'extracted_data': info.to_dict()
                }), 422

            # Return JSON response if requested
            if response_format == 'json':
                return jsonify({
                    'success': True,
                    'data': info.to_dict(),
                    'formatted': {
                        'from': info.from_station,
                        'to': info.to_station,
                        'departure': info.get_formatted_departure(),
                        'arrival': info.get_formatted_arrival(),
                        'train': f"{info.train_type} {info.train_number}" if info.train_type and info.train_number else None,
                    }
                })

            # Generate ICS file
            ics_data = create_ics_bytes(info)

            # Create response with ICS file
            output_filename = f"DSB_Rejse_{info.get_formatted_departure().replace(' ', '_').replace(':', '-')}.ics" \
                if info.get_formatted_departure() else 'DSB_Rejse.ics'

            # Write ICS to temporary file for sending
            temp_ics = Path(app.config['UPLOAD_FOLDER']) / output_filename
            temp_ics.write_bytes(ics_data)

            return send_file(
                temp_ics,
                as_attachment=True,
                download_name=output_filename,
                mimetype='text/calendar'
            )

        finally:
            # Clean up temporary PDF
            if temp_pdf.exists():
                temp_pdf.unlink()

    except FileNotFoundError as e:
        return jsonify({
            'error': 'File not found',
            'message': str(e)
        }), 404

    except TicketParsingError as e:
        return jsonify({
            'error': 'Parsing error',
            'message': f'Failed to parse ticket PDF: {str(e)}'
        }), 422

    except CalendarGenerationError as e:
        return jsonify({
            'error': 'Calendar generation error',
            'message': f'Failed to generate calendar: {str(e)}'
        }), 500

    except Exception as e:
        app.logger.error(f"Unexpected error: {e}", exc_info=True)
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred. Please try again.'
        }), 500


@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error"""
    return jsonify({
        'error': 'File too large',
        'message': 'Maximum file size is 16MB'
    }), 413


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Not found',
        'message': 'The requested resource was not found'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    app.logger.error(f"Internal error: {error}", exc_info=True)
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500


if __name__ == '__main__':
    # Get configuration from environment
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))

    app.run(host=host, port=port, debug=debug)
