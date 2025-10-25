from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from models.data_processor import DataProcessor
from models.recommendation_model import RecommendationModel
from agents.agentic_orchestrator import agentic_orchestrator
from database import db_manager
from config import config
import os
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(config['development'])

# Initialize components
data_processor = DataProcessor('data/student_data.csv')
recommendation_model = RecommendationModel()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recommendation-form')
def recommendation_form():
    # Get available options for dropdowns
    options = data_processor.get_available_options()
    return render_template('student_form.html', options=options)

@app.route('/get-recommendation', methods=['POST'])
def get_recommendation():
    try:
        logger.info("Received recommendation request")
        
        # Get form data with enhanced fields
        student_data = {
            'name': request.form.get('name', '').strip(),
            'mobile_number': request.form.get('mobile_number', '').strip(),
            'email': request.form.get('email', '').strip(),
            'education_type': request.form.get('education_type'),
            'ssc_percent': float(request.form.get('ssc_percent', 0)),
            'hsc_percent': float(request.form.get('hsc_percent', 0) or 0),
            'diploma_percent': float(request.form.get('diploma_percent', 0) or 0),
            'subjects': request.form.get('subjects'),
            'interests': request.form.getlist('interests'),
            'preferred_field': request.form.get('preferred_field'),
            'preferred_mode': request.form.get('preferred_mode'),
            'budget': float(request.form.get('budget', 0)),
            'location_preference': request.form.get('location_preference')
        }
        
        logger.info(f"Processing recommendation for student: {student_data.get('name', 'Anonymous')}")
        
        # Validate required fields
        required_fields = ['name', 'mobile_number', 'education_type', 'subjects', 'preferred_field', 'preferred_mode', 'location_preference']
        missing_fields = [field for field in required_fields if not student_data[field]]
        
        if missing_fields:
            flash(f"Missing required fields: {', '.join(missing_fields)}", 'error')
            return redirect(url_for('recommendation_form'))
        
        # Create combined features for similarity search (legacy support)
        combined_features = data_processor.combine_features(student_data)
        similar_students = data_processor.get_similar_students(combined_features, top_n=5)
        
        # Use Agentic AI Orchestrator for advanced processing
        logger.info("Starting agentic AI processing")
        agentic_result = agentic_orchestrator.process_student_request(student_data, similar_students)
        
        if 'error' in agentic_result:
            logger.error(f"Agentic processing failed: {agentic_result['error']}")
            flash(f"Recommendation generation failed: {agentic_result['error']}", 'error')
            return redirect(url_for('recommendation_form'))
        
        # Extract results from agentic processing
        analysis_data = agentic_result.get('analysis_data', {})
        recommendation = agentic_result.get('recommendation', {})
        validation = agentic_result.get('validation', {})
        
        # Prepare response data
        response_data = {
            'student_data': student_data,
            'analysis_data': analysis_data,
            'recommendation': recommendation,
            'validation': validation,
            'similar_students': similar_students[:3] if similar_students else [],
            'processing_time': agentic_result.get('processing_time', 0),
            'student_id': agentic_result.get('student_id'),
            'recommendation_id': agentic_result.get('recommendation_id')
        }
        
        logger.info(f"Successfully generated recommendation for student {agentic_result.get('student_id')}")
        
        return render_template('recommendation.html', **response_data)
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Error in recommendation generation: {str(e)}")
        logger.error(f"Traceback: {error_details}")
        flash(f"An error occurred: {str(e)}", 'error')
        return redirect(url_for('recommendation_form'))

@app.route('/api/recommend', methods=['POST'])
def api_recommend():
    """API endpoint for programmatic access"""
    try:
        data = request.get_json()
        
        student_data = {
            'education_type': data.get('education_type'),
            'ssc_percent': float(data.get('ssc_percent', 0)),
            'hsc_percent': float(data.get('hsc_percent', 0)),
            'diploma_percent': float(data.get('diploma_percent', 0)),
            'subjects': data.get('subjects'),
            'interests': data.get('interests', []),
            'preferred_field': data.get('preferred_field'),
            'preferred_mode': data.get('preferred_mode'),
            'budget': float(data.get('budget', 0)),
            'location_preference': data.get('location_preference')
        }
        
        combined_features = data_processor.combine_features(student_data)
        similar_students = data_processor.get_similar_students(combined_features)
        
        pathway_label = similar_students[0].get('pathway_label') if similar_students else None
        pathway_stats = data_processor.get_pathway_stats(pathway_label) if pathway_label else None
        
        ai_recommendation = recommendation_model.generate_personalized_recommendation(
            student_data, similar_students, pathway_stats
        )
        
        return jsonify({
            'recommendation': ai_recommendation,
            'similar_profiles': similar_students[:3],
            'pathway_statistics': pathway_stats
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/pathway-insights')
def pathway_insights():
    """Show insights about different pathways"""
    pathway_insights = {}
    for label in data_processor.df['pathway_label'].unique():
        pathway_insights[label] = data_processor.get_pathway_stats(label)
    
    return render_template('insights.html', pathway_insights=pathway_insights)

@app.route('/dashboard')
def dashboard():
    """Admin dashboard with analytics"""
    try:
        analytics = agentic_orchestrator.get_analytics()
        return render_template('dashboard.html', analytics=analytics)
    except Exception as e:
        logger.error(f"Error loading dashboard: {e}")
        flash(f"Error loading dashboard: {e}", 'error')
        return redirect(url_for('index'))

@app.route('/api/health')
def api_health():
    """API endpoint for health check"""
    try:
        health_status = agentic_orchestrator.health_check()
        return jsonify(health_status)
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics')
def api_analytics():
    """API endpoint for analytics"""
    try:
        analytics = agentic_orchestrator.get_analytics()
        return jsonify(analytics)
    except Exception as e:
        logger.error(f"Analytics request failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/learning-insights')
def api_learning_insights():
    """API endpoint for reinforcement learning insights"""
    try:
        insights = agentic_orchestrator.get_learning_insights()
        return jsonify(insights)
    except Exception as e:
        logger.error(f"Learning insights request failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/feedback', methods=['POST'])
def submit_feedback():
    """Submit feedback for a recommendation and learn from it"""
    try:
        data = request.get_json()
        student_id = data.get('student_id')
        recommendation_id = data.get('recommendation_id')
        rating = data.get('rating')
        feedback_text = data.get('feedback_text', '')
        
        if not all([student_id, recommendation_id, rating]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Save feedback to database
        feedback_id = db_manager.add_feedback(student_id, recommendation_id, rating, feedback_text)
        
        # Get student data and recommendation for learning
        try:
            student_data = db_manager.get_student_by_id(student_id)
            recommendation_data = db_manager.get_recommendation_by_id(recommendation_id)
            
            if student_data and recommendation_data:
                # Prepare feedback data for reinforcement learning
                feedback_data = {
                    'rating': rating,
                    'feedback_text': feedback_text,
                    'recommendation_used': rating >= 3,  # Assume rating >= 3 means recommendation was useful
                    'pathway_followed': rating >= 4,  # Assume rating >= 4 means they might follow the pathway
                    'is_valid': rating >= 2,  # Assume rating >= 2 means recommendation was valid
                    'response_time': 0  # Could be tracked from the original request
                }
                
                # Learn from feedback using reinforcement learning
                agentic_orchestrator.learn_from_feedback(
                    student_data, recommendation_data, feedback_data
                )
                
                logger.info(f"Learned from feedback: rating={rating}, student_id={student_id}")
                
        except Exception as e:
            logger.error(f"Error in reinforcement learning from feedback: {e}")
            # Don't fail the feedback submission if learning fails
        
        return jsonify({
            'success': True,
            'feedback_id': feedback_id,
            'message': 'Feedback submitted successfully and learned from'
        })
        
    except Exception as e:
        logger.error(f"Feedback submission failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/students')
def students_list():
    """List all students (admin view)"""
    try:
        page = int(request.args.get('page', 1))
        per_page = 20
        offset = (page - 1) * per_page
        
        students = db_manager.get_all_students(limit=per_page, offset=offset)
        return render_template('students_list.html', students=students, page=page)
        
    except Exception as e:
        logger.error(f"Error loading students list: {e}")
        flash(f"Error loading students: {e}", 'error')
        return redirect(url_for('index'))

@app.route('/student/<int:student_id>')
def student_detail(student_id):
    """View student details and recommendations"""
    try:
        student = db_manager.get_student_by_id(student_id)
        if not student:
            flash('Student not found', 'error')
            return redirect(url_for('students_list'))
        
        recommendations = db_manager.get_student_recommendations(student_id)
        
        return render_template('student_detail.html', 
                             student=student, 
                             recommendations=recommendations)
        
    except Exception as e:
        logger.error(f"Error loading student details: {e}")
        flash(f"Error loading student details: {e}", 'error')
        return redirect(url_for('students_list'))

if __name__ == '__main__':
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5000)