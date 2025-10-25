import sqlite3
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
import json

class DatabaseManager:
    def __init__(self, db_path: str = "student_pathway.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Students table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                mobile_number TEXT NOT NULL,
                email TEXT,
                education_type TEXT NOT NULL,
                ssc_percent REAL,
                hsc_percent REAL,
                diploma_percent REAL,
                subjects TEXT,
                interests TEXT,
                preferred_field TEXT,
                preferred_mode TEXT,
                budget REAL,
                location_preference TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Recommendations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                recommended_pathway TEXT,
                reasoning TEXT,
                career_opportunities TEXT,
                suggested_courses TEXT,
                skills_to_develop TEXT,
                additional_recommendations TEXT,
                confidence_score REAL,
                similar_students_data TEXT,
                pathway_stats TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students (id)
            )
        ''')
        
        # Feedback table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                recommendation_id INTEGER,
                rating INTEGER CHECK (rating >= 1 AND rating <= 5),
                feedback_text TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students (id),
                FOREIGN KEY (recommendation_id) REFERENCES recommendations (id)
            )
        ''')
        
        # Analytics table for tracking usage
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                event_data TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        print("Database initialized successfully")
    
    def add_student(self, student_data: Dict[str, Any]) -> int:
        """Add a new student to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Convert interests list to JSON string
        interests_json = json.dumps(student_data.get('interests', []))
        
        cursor.execute('''
            INSERT INTO students (
                name, mobile_number, email, education_type, ssc_percent, 
                hsc_percent, diploma_percent, subjects, interests, 
                preferred_field, preferred_mode, budget, location_preference
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            student_data['name'],
            student_data['mobile_number'],
            student_data.get('email', ''),
            student_data['education_type'],
            student_data.get('ssc_percent', 0),
            student_data.get('hsc_percent', 0),
            student_data.get('diploma_percent', 0),
            student_data.get('subjects', ''),
            interests_json,
            student_data.get('preferred_field', ''),
            student_data.get('preferred_mode', ''),
            student_data.get('budget', 0),
            student_data.get('location_preference', '')
        ))
        
        student_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Log analytics
        self.log_analytics('student_registered', {'student_id': student_id})
        
        return student_id
    
    def save_recommendation(self, student_id: int, recommendation_data: Dict[str, Any]) -> int:
        """Save a recommendation for a student"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO recommendations (
                student_id, recommended_pathway, reasoning, career_opportunities,
                suggested_courses, skills_to_develop, additional_recommendations,
                confidence_score, similar_students_data, pathway_stats
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            student_id,
            recommendation_data.get('recommended_pathway', ''),
            recommendation_data.get('reasoning', ''),
            json.dumps(recommendation_data.get('career_opportunities', [])),
            json.dumps(recommendation_data.get('suggested_courses', [])),
            json.dumps(recommendation_data.get('skills_to_develop', [])),
            recommendation_data.get('additional_recommendations', ''),
            recommendation_data.get('confidence_score', 0.0),
            json.dumps(recommendation_data.get('similar_students_data', [])),
            json.dumps(recommendation_data.get('pathway_stats', {}))
        ))
        
        recommendation_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Log analytics
        self.log_analytics('recommendation_generated', {
            'student_id': student_id,
            'recommendation_id': recommendation_id
        })
        
        return recommendation_id
    
    def get_student_by_id(self, student_id: int) -> Optional[Dict[str, Any]]:
        """Get student data by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM students WHERE id = ?', (student_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            columns = [description[0] for description in cursor.description]
            student_data = dict(zip(columns, row))
            # Parse interests JSON
            student_data['interests'] = json.loads(student_data['interests'])
            return student_data
        return None
    
    def get_student_recommendations(self, student_id: int) -> List[Dict[str, Any]]:
        """Get all recommendations for a student"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM recommendations 
            WHERE student_id = ? 
            ORDER BY created_at DESC
        ''', (student_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        recommendations = []
        for row in rows:
            columns = [description[0] for description in cursor.description]
            rec_data = dict(zip(columns, row))
            # Parse JSON fields
            rec_data['career_opportunities'] = json.loads(rec_data['career_opportunities'])
            rec_data['suggested_courses'] = json.loads(rec_data['suggested_courses'])
            rec_data['skills_to_develop'] = json.loads(rec_data['skills_to_develop'])
            rec_data['similar_students_data'] = json.loads(rec_data['similar_students_data'])
            rec_data['pathway_stats'] = json.loads(rec_data['pathway_stats'])
            recommendations.append(rec_data)
        
        return recommendations
    
    def add_feedback(self, student_id: int, recommendation_id: int, 
                    rating: int, feedback_text: str = "") -> int:
        """Add feedback for a recommendation"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO feedback (student_id, recommendation_id, rating, feedback_text)
            VALUES (?, ?, ?, ?)
        ''', (student_id, recommendation_id, rating, feedback_text))
        
        feedback_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Log analytics
        self.log_analytics('feedback_submitted', {
            'student_id': student_id,
            'recommendation_id': recommendation_id,
            'rating': rating
        })
        
        return feedback_id
    
    def log_analytics(self, event_type: str, event_data: Dict[str, Any]):
        """Log analytics events"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO analytics (event_type, event_data)
            VALUES (?, ?)
        ''', (event_type, json.dumps(event_data)))
        
        conn.commit()
        conn.close()
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get analytics summary for dashboard"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total students
        cursor.execute('SELECT COUNT(*) FROM students')
        total_students = cursor.fetchone()[0]
        
        # Total recommendations
        cursor.execute('SELECT COUNT(*) FROM recommendations')
        total_recommendations = cursor.fetchone()[0]
        
        # Average rating
        cursor.execute('SELECT AVG(rating) FROM feedback WHERE rating IS NOT NULL')
        avg_rating = cursor.fetchone()[0] or 0
        
        # Recent activity (last 7 days)
        cursor.execute('''
            SELECT COUNT(*) FROM students 
            WHERE created_at >= datetime('now', '-7 days')
        ''')
        recent_students = cursor.fetchone()[0]
        
        # Popular fields
        cursor.execute('''
            SELECT preferred_field, COUNT(*) as count 
            FROM students 
            GROUP BY preferred_field 
            ORDER BY count DESC 
            LIMIT 5
        ''')
        popular_fields = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            'total_students': total_students,
            'total_recommendations': total_recommendations,
            'average_rating': round(avg_rating, 2),
            'recent_students': recent_students,
            'popular_fields': popular_fields
        }
    
    def get_all_students(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all students with pagination"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM students 
            ORDER BY created_at DESC 
            LIMIT ? OFFSET ?
        ''', (limit, offset))
        
        rows = cursor.fetchall()
        conn.close()
        
        students = []
        for row in rows:
            columns = [description[0] for description in cursor.description]
            student_data = dict(zip(columns, row))
            student_data['interests'] = json.loads(student_data['interests'])
            students.append(student_data)
        
        return students

# Global database instance
db_manager = DatabaseManager()
