import os
from datetime import datetime
import logging

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from whitenoise import WhiteNoise
from utils.interview_generator import InterviewGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__, static_folder='../frontend', static_url_path='')
app.wsgi_app = WhiteNoise(app.wsgi_app, root='../frontend', prefix='')

# Configure CORS
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Store interview sessions
interview_sessions = {}
FRONTEND_DIR = '../frontend'


@app.route('/')
def serve_frontend():
    """Serve the main frontend HTML file."""
    try:
        return send_from_directory(FRONTEND_DIR, 'index.html')
    except Exception as e:
        logger.error(f"Error serving frontend: {str(e)}")
        return jsonify({'error': 'Frontend not found'}), 404


@app.route('/<path:path>')
def serve_static(path):
    """Serve static frontend files."""
    try:
        return send_from_directory(FRONTEND_DIR, path)
    except Exception as e:
        logger.error(f"Error serving static file {path}: {str(e)}")
        return jsonify({'error': 'File not found'}), 404


@app.route('/api/start_interview', methods=['POST'])
def start_interview():
    """Start a new interview session."""
    try:
        data = request.get_json()
        if data is None:
            return jsonify({
                'success': False,
                'error': 'Invalid JSON data'
            }), 400

        session_id = data.get('session_id', 'default')
        job_role = data.get('job_role', '')
        
        logger.info(f"Starting interview for {job_role} - Session: {session_id}")

        # Clean up existing session
        if session_id in interview_sessions:
            del interview_sessions[session_id]

        generator = InterviewGenerator()
        
        # Generate questions based on user input
        questions = generator.start_interview(data)
        
        # Log the number of questions generated
        logger.info(f"Generated {len(questions)} questions for {job_role}")
        for i, q in enumerate(questions, 1):
            logger.info(f"  Q{i}: {q}")
        
        interview_sessions[session_id] = generator

        # Get first question
        first_question = generator.get_next_question()

        if first_question is None:
            logger.error(f"Failed to get first question for {job_role}")
            return jsonify({
                'success': False,
                'error': 'Failed to generate initial question'
            }), 500

        logger.info(f"First question: {first_question['question']}")
        
        return jsonify({
            'success': True,
            'question': first_question,
            'session_id': session_id,
            'total_questions': len(questions)
        })
    except Exception as e:
        logger.error(f"Error in start_interview: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@app.route('/api/get_next_question', methods=['POST'])
def get_next_question():
    """Get the next question in the interview."""
    try:
        data = request.get_json()
        if data is None:
            return jsonify({
                'success': False,
                'error': 'Invalid JSON data'
            }), 400

        session_id = data.get('session_id', 'default')
        generator = interview_sessions.get(session_id)

        if generator is None:
            return jsonify({
                'success': False,
                'error': 'Session not found'
            }), 404

        next_question = generator.get_next_question()

        if next_question is not None:
            logger.info(f"Next question: {next_question['question']}")
            return jsonify({
                'success': True,
                'question': next_question
            })

        return jsonify({
            'success': True,
            'complete': True,
            'message': 'Interview completed'
        })
    except Exception as e:
        logger.error(f"Error in get_next_question: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@app.route('/api/submit_answer', methods=['POST'])
def submit_answer():
    """Submit an answer for the current question."""
    try:
        data = request.get_json()
        if data is None:
            return jsonify({
                'success': False,
                'error': 'Invalid JSON data'
            }), 400

        session_id = data.get('session_id', 'default')
        question = data.get('question')
        answer = data.get('answer')

        if question is None or answer is None:
            return jsonify({
                'success': False,
                'error': 'Missing required fields'
            }), 400

        generator = interview_sessions.get(session_id)
        if generator is None:
            return jsonify({
                'success': False,
                'error': 'Session not found'
            }), 404

        evaluation = generator.evaluate_answer(question, answer)
        is_complete = generator.is_interview_complete()

        logger.info(f"Score for question: {evaluation.get('score', 0)}")
        
        return jsonify({
            'success': True,
            'evaluation': evaluation,
            'is_complete': is_complete
        })
    except Exception as e:
        logger.error(f"Error in submit_answer: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@app.route('/api/get_report', methods=['POST'])
def get_report():
    """Get the final interview report."""
    try:
        data = request.get_json()
        if data is None:
            return jsonify({
                'success': False,
                'error': 'Invalid JSON data'
            }), 400

        session_id = data.get('session_id', 'default')
        generator = interview_sessions.get(session_id)

        if generator is None:
            return jsonify({
                'success': False,
                'error': 'Session not found'
            }), 404

        report = generator.get_final_report()
        overall_score = generator.get_overall_score()
        interview_data = generator.get_interview_data()

        return jsonify({
            'success': True,
            'report': report,
            'overall_score': overall_score,
            'interview_data': interview_data
        })
    except Exception as e:
        logger.error(f"Error in get_report: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@app.route('/api/end_interview', methods=['POST'])
def end_interview():
    """End an interview session and clean up resources."""
    try:
        data = request.get_json()
        if data is None:
            return jsonify({
                'success': False,
                'error': 'Invalid JSON data'
            }), 400

        session_id = data.get('session_id', 'default')

        if session_id in interview_sessions:
            del interview_sessions[session_id]
            return jsonify({
                'success': True,
                'message': 'Session ended successfully'
            })

        return jsonify({
            'success': False,
            'error': 'Session not found'
        }), 404
    except Exception as e:
        logger.error(f"Error in end_interview: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring."""
    return jsonify({
        'status': 'healthy',
        'active_sessions': len(interview_sessions),
        'timestamp': datetime.now().isoformat()
    })


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'success': False,
        'error': 'Resource not found'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    logger.info(f"Starting Flask application on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug_mode)