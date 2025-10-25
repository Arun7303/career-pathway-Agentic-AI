from .base_agent import BaseAgent
from typing import Dict, Any, List
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import json

class DataAnalysisAgent(BaseAgent):
    """Agent responsible for analyzing student data and extracting insights"""
    
    def __init__(self):
        super().__init__("DataAnalysisAgent")
        self.scaler = StandardScaler()
        self.cluster_model = None
        self.pca_model = None
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze student data and return insights"""
        try:
            # Extract student profile
            student_profile = data.get('student_data', {})
            
            # Perform academic analysis
            academic_analysis = self._analyze_academic_performance(student_profile)
            
            # Perform interest analysis
            interest_analysis = self._analyze_interests(student_profile)
            
            # Perform preference analysis
            preference_analysis = self._analyze_preferences(student_profile)
            
            # Generate AI insights
            ai_insights = self._generate_ai_insights(student_profile, {
                'academic': academic_analysis,
                'interests': interest_analysis,
                'preferences': preference_analysis
            })
            
            return {
                'academic_analysis': academic_analysis,
                'interest_analysis': interest_analysis,
                'preference_analysis': preference_analysis,
                'ai_insights': ai_insights,
                'confidence_score': self._calculate_confidence_score(student_profile)
            }
            
        except Exception as e:
            self.logger.error(f"Error in data analysis: {e}")
            return {'error': str(e)}
    
    def _analyze_academic_performance(self, student_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze academic performance and categorize student"""
        ssc_percent = student_profile.get('ssc_percent', 0)
        hsc_percent = student_profile.get('hsc_percent', 0)
        diploma_percent = student_profile.get('diploma_percent', 0)
        
        # Calculate average performance
        scores = [score for score in [ssc_percent, hsc_percent, diploma_percent] if score > 0]
        avg_score = np.mean(scores) if scores else 0
        
        # Categorize performance
        if avg_score >= 90:
            performance_level = "Excellent"
            recommendation_priority = "High"
        elif avg_score >= 80:
            performance_level = "Very Good"
            recommendation_priority = "High"
        elif avg_score >= 70:
            performance_level = "Good"
            recommendation_priority = "Medium"
        elif avg_score >= 60:
            performance_level = "Average"
            recommendation_priority = "Medium"
        else:
            performance_level = "Below Average"
            recommendation_priority = "Low"
        
        return {
            'average_score': round(avg_score, 2),
            'performance_level': performance_level,
            'recommendation_priority': recommendation_priority,
            'score_distribution': {
                'ssc': ssc_percent,
                'hsc': hsc_percent,
                'diploma': diploma_percent
            },
            'strengths': self._identify_academic_strengths(student_profile),
            'improvement_areas': self._identify_improvement_areas(student_profile)
        }
    
    def _analyze_interests(self, student_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze student interests and categorize them"""
        interests = student_profile.get('interests', [])
        
        # Categorize interests
        interest_categories = {
            'technical': ['Data Science', 'AI', 'Cybersecurity', 'Web Development', 'Robotics'],
            'creative': ['Design', 'UX', 'Marketing'],
            'analytical': ['Research', 'Finance', 'Management'],
            'social': ['Psychology', 'Management']
        }
        
        categorized_interests = {}
        for category, category_interests in interest_categories.items():
            categorized_interests[category] = [interest for interest in interests if interest in category_interests]
        
        # Determine primary interest category
        primary_category = max(categorized_interests.keys(), 
                             key=lambda k: len(categorized_interests[k])) if interests else 'general'
        
        return {
            'all_interests': interests,
            'categorized_interests': categorized_interests,
            'primary_category': primary_category,
            'interest_diversity_score': len(set(interests)) / len(interests) if interests else 0,
            'recommended_focus_areas': self._recommend_focus_areas(categorized_interests)
        }
    
    def _analyze_preferences(self, student_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze student preferences and constraints"""
        preferred_field = student_profile.get('preferred_field', '')
        preferred_mode = student_profile.get('preferred_mode', '')
        budget = student_profile.get('budget', 0)
        location = student_profile.get('location_preference', '')
        
        # Analyze budget constraints
        budget_category = self._categorize_budget(budget)
        
        # Analyze mode preferences
        mode_analysis = self._analyze_mode_preference(preferred_mode)
        
        return {
            'field_preference': preferred_field,
            'mode_preference': preferred_mode,
            'budget_analysis': {
                'amount': budget,
                'category': budget_category,
                'affordability_score': self._calculate_affordability_score(budget)
            },
            'location_preference': location,
            'mode_analysis': mode_analysis,
            'constraints': self._identify_constraints(student_profile)
        }
    
    def _generate_ai_insights(self, student_profile: Dict[str, Any], 
                            analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI-powered insights about the student"""
        if not self.is_available:
            return self._fallback_insights(student_profile, analysis_data)
        
        prompt = f"""
        ROLE: You are an expert educational psychologist and career counselor analyzing a student's profile. You have deep knowledge of learning psychology, career development, and the Indian education system.

        STUDENT PROFILE:
        - Name: {student_profile.get('name', 'Student')}
        - Academic Performance: {analysis_data['academic']['performance_level']} (Average: {analysis_data['academic']['average_score']}%)
        - SSC Score: {student_profile.get('ssc_percent', 0)}%
        - HSC Score: {student_profile.get('hsc_percent', 0)}%
        - Primary Interest Category: {analysis_data['interests']['primary_category']}
        - Specific Interests: {', '.join(analysis_data['interests']['all_interests'])}
        - Preferred Field: {analysis_data['preferences']['field_preference']}
        - Budget Category: {analysis_data['preferences']['budget_analysis']['category']} ({student_profile.get('budget', 0)} lakhs/year)
        - Learning Mode: {analysis_data['preferences']['mode_preference']}
        - Location: {student_profile.get('location_preference', 'Not specified')}

        TASK: Provide deep psychological and educational insights about this student's learning style, motivation patterns, and optimal educational approach. Consider their specific interests in {', '.join(student_profile.get('interests', []))} and their academic performance.

        REQUIREMENTS:
        1. Analyze the student's learning style based on their profile and interests
        2. Identify their motivation patterns and drivers
        3. Suggest optimal learning approaches for their interests
        4. Identify potential challenges and how to address them
        5. Recommend personality-aligned career paths
        6. Consider their budget constraints and location preferences
        7. Analyze their academic strengths and areas for improvement

        FORMAT YOUR RESPONSE AS JSON:
        {{
            "learning_style": "Detailed analysis of learning style based on their interests and academic performance",
            "motivation_patterns": "Analysis of what motivates this student, considering their specific interests",
            "optimal_learning_approach": "Recommended learning methodology tailored to their interests and learning style",
            "potential_challenges": ["Specific Challenge 1", "Specific Challenge 2", "Specific Challenge 3"],
            "personality_insights": "Deep personality analysis considering their interests and academic profile",
            "career_alignment": "How their personality and interests align with career choices",
            "strengths": ["Specific Strength 1", "Specific Strength 2", "Specific Strength 3"],
            "improvement_areas": ["Specific Area 1", "Specific Area 2"],
            "recommended_learning_resources": ["Resource 1", "Resource 2", "Resource 3"],
            "study_habits": "Recommended study habits based on their profile"
        }}
        """
        
        response = self.generate_response(prompt)
        if response:
            parsed_response = self.parse_json_response(response)
            if parsed_response:
                return parsed_response
        
        return self._fallback_insights(student_profile, analysis_data)
    
    def _fallback_insights(self, student_profile: Dict[str, Any], 
                          analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback insights when AI is not available"""
        return {
            "learning_style": "Mixed learning style based on academic performance and interests",
            "motivation_patterns": "Motivated by practical applications and career relevance",
            "optimal_learning_approach": "Hands-on learning with theoretical foundation",
            "potential_challenges": ["Time management", "Balancing multiple interests", "Budget constraints"],
            "personality_insights": "Analytical and goal-oriented student with diverse interests",
            "career_alignment": "Well-suited for interdisciplinary fields combining technical and creative elements"
        }
    
    def _identify_academic_strengths(self, student_profile: Dict[str, Any]) -> List[str]:
        """Identify academic strengths based on scores"""
        strengths = []
        ssc = student_profile.get('ssc_percent', 0)
        hsc = student_profile.get('hsc_percent', 0)
        diploma = student_profile.get('diploma_percent', 0)
        
        if ssc >= 85:
            strengths.append("Strong foundation in secondary education")
        if hsc >= 85:
            strengths.append("Excellent higher secondary performance")
        if diploma >= 85:
            strengths.append("Outstanding diploma performance")
        
        return strengths
    
    def _identify_improvement_areas(self, student_profile: Dict[str, Any]) -> List[str]:
        """Identify areas for improvement"""
        improvements = []
        ssc = student_profile.get('ssc_percent', 0)
        hsc = student_profile.get('hsc_percent', 0)
        diploma = student_profile.get('diploma_percent', 0)
        
        if ssc < 70:
            improvements.append("Foundation knowledge strengthening needed")
        if hsc < 70:
            improvements.append("Higher secondary concepts review required")
        if diploma < 70:
            improvements.append("Diploma-level skills enhancement needed")
        
        return improvements
    
    def _recommend_focus_areas(self, categorized_interests: Dict[str, List[str]]) -> List[str]:
        """Recommend focus areas based on interests"""
        focus_areas = []
        
        if categorized_interests.get('technical'):
            focus_areas.append("Technical skill development")
        if categorized_interests.get('creative'):
            focus_areas.append("Creative and design thinking")
        if categorized_interests.get('analytical'):
            focus_areas.append("Analytical and research skills")
        if categorized_interests.get('social'):
            focus_areas.append("Interpersonal and communication skills")
        
        return focus_areas
    
    def _categorize_budget(self, budget: float) -> str:
        """Categorize budget into levels"""
        if budget >= 10:
            return "High"
        elif budget >= 5:
            return "Medium"
        elif budget >= 2:
            return "Low"
        else:
            return "Very Low"
    
    def _calculate_affordability_score(self, budget: float) -> float:
        """Calculate affordability score (0-1)"""
        return min(budget / 10.0, 1.0)
    
    def _analyze_mode_preference(self, mode: str) -> Dict[str, Any]:
        """Analyze learning mode preference"""
        mode_benefits = {
            'Online': ['Flexibility', 'Cost-effective', 'Self-paced learning'],
            'Offline': ['Direct interaction', 'Structured environment', 'Peer learning'],
            'Hybrid': ['Best of both worlds', 'Flexibility with structure', 'Adaptable learning']
        }
        
        return {
            'preferred_mode': mode,
            'benefits': mode_benefits.get(mode, []),
            'suitability_score': 0.8  # Default score
        }
    
    def _identify_constraints(self, student_profile: Dict[str, Any]) -> List[str]:
        """Identify potential constraints"""
        constraints = []
        
        budget = student_profile.get('budget', 0)
        if budget < 3:
            constraints.append("Limited budget for expensive programs")
        
        location = student_profile.get('location_preference', '')
        if location in ['Remote', 'Rural']:
            constraints.append("Limited access to premium institutions")
        
        return constraints
    
    def _calculate_confidence_score(self, student_profile: Dict[str, Any]) -> float:
        """Calculate confidence score for the analysis"""
        score = 0.5  # Base score
        
        # Increase score based on data completeness
        if student_profile.get('ssc_percent', 0) > 0:
            score += 0.1
        if student_profile.get('hsc_percent', 0) > 0 or student_profile.get('diploma_percent', 0) > 0:
            score += 0.1
        if student_profile.get('interests'):
            score += 0.1
        if student_profile.get('preferred_field'):
            score += 0.1
        if student_profile.get('budget', 0) > 0:
            score += 0.1
        
        return min(score, 1.0)
