from .base_agent import BaseAgent
from typing import Dict, Any, List
import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd

class RecommendationAgent(BaseAgent):
    """Agent responsible for generating personalized pathway recommendations"""
    
    def __init__(self):
        super().__init__("RecommendationAgent")
        self.tfidf_vectorizer = TfidfVectorizer(max_features=200, stop_words='english')
        self.pathway_database = self._load_pathway_database()
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate personalized pathway recommendations"""
        try:
            student_data = data.get('student_data', {})
            analysis_data = data.get('analysis_data', {})
            similar_students = data.get('similar_students', [])
            
            # Generate multiple recommendation strategies
            ai_recommendation = self._generate_ai_recommendation(student_data, analysis_data, similar_students)
            similarity_recommendation = self._generate_similarity_recommendation(similar_students)
            field_based_recommendation = self._generate_field_based_recommendation(student_data)
            
            # Combine and rank recommendations
            final_recommendation = self._combine_recommendations(
                ai_recommendation, similarity_recommendation, field_based_recommendation
            )
            
            # Add confidence scoring
            final_recommendation['confidence_score'] = self._calculate_recommendation_confidence(
                student_data, similar_students, analysis_data
            )
            
            return final_recommendation
            
        except Exception as e:
            self.logger.error(f"Error in recommendation generation: {e}")
            return {'error': str(e)}
    
    def _generate_ai_recommendation(self, student_data: Dict[str, Any], 
                                  analysis_data: Dict[str, Any], 
                                  similar_students: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate AI-powered recommendation using Google Gemini"""
        if not self.is_available:
            return self._fallback_recommendation(student_data, similar_students)
        
        prompt = self._create_advanced_prompt(student_data, analysis_data, similar_students)
        response = self.generate_response(prompt)
        
        if response:
            parsed_response = self.parse_json_response(response)
            if parsed_response:
                return parsed_response
        
        return self._fallback_recommendation(student_data, similar_students)
    
    def _create_advanced_prompt(self, student_data: Dict[str, Any], 
                              analysis_data: Dict[str, Any], 
                              similar_students: List[Dict[str, Any]]) -> str:
        """Create advanced prompt for AI recommendation"""
        
        # Format academic background
        academic_info = f"""
        Academic Performance: {analysis_data.get('academic_analysis', {}).get('performance_level', 'Unknown')}
        Average Score: {analysis_data.get('academic_analysis', {}).get('average_score', 0)}%
        Strengths: {', '.join(analysis_data.get('academic_analysis', {}).get('strengths', []))}
        """
        
        # Format interest analysis
        interest_info = f"""
        Primary Interest Category: {analysis_data.get('interest_analysis', {}).get('primary_category', 'General')}
        All Interests: {', '.join(analysis_data.get('interest_analysis', {}).get('all_interests', []))}
        Recommended Focus Areas: {', '.join(analysis_data.get('interest_analysis', {}).get('recommended_focus_areas', []))}
        """
        
        # Format preference analysis
        preference_info = f"""
        Preferred Field: {analysis_data.get('preference_analysis', {}).get('field_preference', 'Not specified')}
        Learning Mode: {analysis_data.get('preference_analysis', {}).get('mode_preference', 'Not specified')}
        Budget Category: {analysis_data.get('preference_analysis', {}).get('budget_analysis', {}).get('category', 'Not specified')}
        Location: {analysis_data.get('preference_analysis', {}).get('location_preference', 'Not specified')}
        """
        
        # Format AI insights
        ai_insights = analysis_data.get('ai_insights', {})
        insights_info = f"""
        Learning Style: {ai_insights.get('learning_style', 'Not analyzed')}
        Motivation Patterns: {ai_insights.get('motivation_patterns', 'Not analyzed')}
        Optimal Learning Approach: {ai_insights.get('optimal_learning_approach', 'Not analyzed')}
        """
        
        # Format similar students
        similar_students_info = self._format_similar_students_for_prompt(similar_students)
        
        prompt = f"""
        ROLE: You are an expert educational pathway advisor and career counselor with deep knowledge of the Indian education system, global trends, and emerging career opportunities. You have access to real-time data about job markets, salary trends, and educational institutions.

        STUDENT PROFILE ANALYSIS:
        
        ACADEMIC BACKGROUND:
        {academic_info}
        
        INTEREST ANALYSIS:
        {interest_info}
        
        PREFERENCE ANALYSIS:
        {preference_info}
        
        PSYCHOLOGICAL INSIGHTS:
        {insights_info}
        
        SIMILAR SUCCESSFUL STUDENTS:
        {similar_students_info}
        
        TASK: Create a comprehensive, personalized educational pathway recommendation that considers:
        1. The student's academic capabilities and performance level
        2. Their specific interests, learning style, and motivation patterns
        3. Budget constraints and location preferences
        4. Current market trends and future job prospects (2024-2030)
        5. Similar students' successful pathways
        6. Emerging fields and technologies
        7. Industry demand and growth projections
        8. Skill gaps in the current market
        
        REQUIREMENTS:
        1. Provide a detailed, step-by-step educational pathway with specific institutions
        2. Include specific degree programs, certifications, and skill development
        3. Suggest 5-7 career opportunities with realistic growth potential and salary ranges
        4. Recommend 4-6 specific courses or programs with institution names
        5. List 6-8 essential skills to develop with learning resources
        6. Provide timeline and milestone recommendations
        7. Include alternative pathways and backup options
        8. Address potential challenges and solutions
        9. Suggest networking and mentorship opportunities
        10. Include realistic cost estimates and funding options
        11. Consider the student's location preference and budget constraints
        
        IMPORTANT: 
        - Be specific about institutions, courses, and career paths
        - Provide realistic salary ranges based on current market data
        - Consider the student's budget of {student_data.get('budget', 0)} lakhs per year
        - Focus on the student's specific interests: {', '.join(student_data.get('interests', []))}
        - Consider their preferred field: {student_data.get('preferred_field', '')}
        - Take into account their location preference: {student_data.get('location_preference', '')}
        
        FORMAT YOUR RESPONSE AS JSON:
        {{
            "recommended_pathway": "Detailed step-by-step pathway description with timeline and specific institutions",
            "reasoning": "Comprehensive explanation of why this pathway is optimal for this specific student, considering their interests, budget, and location",
            "career_opportunities": [
                {{
                    "title": "Specific Career Title",
                    "description": "Detailed description of the role and responsibilities",
                    "growth_potential": "High/Medium/Low with percentage growth",
                    "salary_range": "Realistic salary range in INR (entry to senior level)",
                    "required_skills": ["Specific Skill 1", "Specific Skill 2", "Specific Skill 3"],
                    "companies": ["Company 1", "Company 2", "Company 3"],
                    "job_market_outlook": "Current and future job market conditions"
                }}
            ],
            "suggested_courses": [
                {{
                    "course_name": "Specific Course Name",
                    "level": "Undergraduate/Postgraduate/Certification",
                    "duration": "Exact duration",
                    "cost_estimate": "Realistic cost range in INR",
                    "institutions": ["Specific Institution 1", "Specific Institution 2"],
                    "admission_requirements": "Specific requirements",
                    "scholarship_opportunities": "Available scholarships"
                }}
            ],
            "skills_to_develop": [
                {{
                    "skill": "Specific Skill Name",
                    "importance": "High/Medium/Low",
                    "development_method": "Specific ways to develop this skill",
                    "timeline": "When to focus on this skill",
                    "resources": ["Resource 1", "Resource 2"],
                    "certification": "Relevant certifications if any"
                }}
            ],
            "timeline_milestones": [
                {{
                    "phase": "Specific Phase Name",
                    "duration": "Exact time period",
                    "goals": ["Specific Goal 1", "Specific Goal 2"],
                    "key_actions": ["Specific Action 1", "Specific Action 2"],
                    "success_metrics": "How to measure success"
                }}
            ],
            "alternative_pathways": [
                {{
                    "pathway_name": "Alternative Pathway Name",
                    "description": "Detailed description",
                    "pros": ["Specific Advantage 1", "Specific Advantage 2"],
                    "cons": ["Specific Disadvantage 1", "Specific Disadvantage 2"],
                    "cost_comparison": "Cost comparison with main pathway"
                }}
            ],
            "challenges_and_solutions": [
                {{
                    "challenge": "Specific Potential Challenge",
                    "solution": "Detailed Recommended Solution",
                    "prevention": "How to prevent this challenge",
                    "resources": "Resources to help overcome this challenge"
                }}
            ],
            "networking_opportunities": [
                {{
                    "opportunity": "Specific Networking Opportunity",
                    "description": "What it involves and how to access it",
                    "benefits": ["Specific Benefit 1", "Specific Benefit 2"],
                    "location": "Where this opportunity is available"
                }}
            ],
            "cost_breakdown": {{
                "total_estimated_cost": "Realistic total cost range in INR",
                "yearly_breakdown": "Cost breakdown by year",
                "funding_options": ["Specific Option 1", "Specific Option 2"],
                "scholarship_opportunities": ["Specific Scholarship 1", "Specific Scholarship 2"],
                "loan_options": "Available education loan options"
            }},
            "additional_recommendations": "Comprehensive advice about preparation, application process, long-term career planning, and specific next steps"
        }}
        
        Make the recommendation highly personalized, practical, and actionable. Consider the Indian education system, current job market trends, emerging technologies, and the student's specific circumstances.
        """
        
        return prompt
    
    def _format_similar_students_for_prompt(self, similar_students: List[Dict[str, Any]]) -> str:
        """Format similar students data for the prompt"""
        if not similar_students:
            return "No similar student profiles found in our database."
        
        formatted = []
        for i, student in enumerate(similar_students[:3], 1):
            formatted.append(f"""
            Student {i} (Similarity Score: {student.get('similarity_score', 0):.2f}):
            - Successful Pathway: {student.get('target_pathway', 'N/A')}
            - Academic Performance: SSC {student.get('ssc_percent', 'N/A')}%, HSC {student.get('hsc_percent', 'N/A')}%, Diploma {student.get('diploma_percent', 'N/A')}%
            - Interests: {', '.join(student.get('interests_processed', []))}
            - Preferred Field: {student.get('preferred_field', 'N/A')}
            - Budget: {student.get('budget', 'N/A')} Lakhs
            - Location: {student.get('location_preference', 'N/A')}
            """)
        
        return '\n'.join(formatted)
    
    def _generate_similarity_recommendation(self, similar_students: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate recommendation based on similar students"""
        if not similar_students:
            return {}
        
        # Analyze pathways of similar students
        pathways = [student.get('target_pathway', '') for student in similar_students]
        pathway_counts = {}
        for pathway in pathways:
            if pathway:
                pathway_counts[pathway] = pathway_counts.get(pathway, 0) + 1
        
        # Get most common pathway
        most_common_pathway = max(pathway_counts.keys(), key=pathway_counts.get) if pathway_counts else ""
        
        return {
            'recommended_pathway': most_common_pathway,
            'reasoning': f"Based on {len(similar_students)} students with similar profiles who successfully pursued this pathway",
            'confidence': len(similar_students) / 10.0  # Simple confidence based on number of similar students
        }
    
    def _generate_field_based_recommendation(self, student_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate recommendation based on preferred field"""
        preferred_field = student_data.get('preferred_field', '')
        
        field_pathways = {
            'Engineering': {
                'pathway': 'B.Tech/B.E. in relevant branch → M.Tech/MS → Industry/Research/PhD',
                'reasoning': 'Standard engineering pathway with strong industry demand'
            },
            'Science': {
                'pathway': 'B.Sc in chosen discipline → M.Sc → PhD/Industry/Research',
                'reasoning': 'Research-oriented pathway with multiple career options'
            },
            'Commerce': {
                'pathway': 'B.Com/BBA → MBA → Professional courses (CA, CS, CMA)',
                'reasoning': 'Business-focused pathway with professional certification options'
            },
            'Arts': {
                'pathway': 'BA in chosen subject → MA → PhD/Teaching/Industry',
                'reasoning': 'Liberal arts pathway with diverse career opportunities'
            },
            'Design': {
                'pathway': 'B.Des → M.Des → Industry/Entrepreneurship',
                'reasoning': 'Creative pathway with strong industry connections'
            },
            'Management': {
                'pathway': 'BBA → MBA → Industry/Entrepreneurship',
                'reasoning': 'Leadership-focused pathway with high earning potential'
            }
        }
        
        return field_pathways.get(preferred_field, {
            'pathway': 'Higher Education → Specialization → Career',
            'reasoning': 'General pathway based on your preferences'
        })
    
    def _combine_recommendations(self, ai_rec: Dict[str, Any], 
                               sim_rec: Dict[str, Any], 
                               field_rec: Dict[str, Any]) -> Dict[str, Any]:
        """Combine multiple recommendation strategies"""
        # Prioritize AI recommendation if available
        if ai_rec and not ai_rec.get('error'):
            return ai_rec
        
        # Fall back to similarity-based recommendation
        if sim_rec and sim_rec.get('recommended_pathway'):
            return {
                'recommended_pathway': sim_rec['recommended_pathway'],
                'reasoning': sim_rec['reasoning'],
                'career_opportunities': [
                    "Industry-specific roles in your field",
                    "Graduate programs and higher studies",
                    "Research and development positions",
                    "Entrepreneurship opportunities"
                ],
                'suggested_courses': [
                    "Foundation courses in your preferred field",
                    "Advanced specialization courses",
                    "Practical skill development programs"
                ],
                'skills_to_develop': [
                    "Core subject knowledge",
                    "Problem-solving abilities",
                    "Communication skills",
                    "Technical expertise",
                    "Industry awareness"
                ],
                'additional_recommendations': "Research specific colleges and admission requirements. Consider talking to current students in similar programs."
            }
        
        # Final fallback to field-based recommendation
        return {
            'recommended_pathway': field_rec.get('pathway', 'Higher Education → Specialization → Career'),
            'reasoning': field_rec.get('reasoning', 'Standard pathway based on your preferences'),
            'career_opportunities': [
                "Various roles in your chosen industry",
                "Higher education and research opportunities",
                "Government sector positions",
                "Entrepreneurial ventures"
            ],
            'suggested_courses': [
                "Undergraduate degree in your field",
                "Postgraduate specialization",
                "Professional certification courses"
            ],
            'skills_to_develop': [
                "Academic excellence",
                "Practical application skills",
                "Industry knowledge",
                "Networking abilities"
            ],
            'additional_recommendations': "Focus on building a strong academic foundation. Explore internship opportunities early in your career."
        }
    
    def _calculate_recommendation_confidence(self, student_data: Dict[str, Any], 
                                          similar_students: List[Dict[str, Any]], 
                                          analysis_data: Dict[str, Any]) -> float:
        """Calculate confidence score for the recommendation"""
        confidence = 0.5  # Base confidence
        
        # Increase confidence based on similar students
        if similar_students:
            avg_similarity = np.mean([s.get('similarity_score', 0) for s in similar_students])
            confidence += avg_similarity * 0.3
        
        # Increase confidence based on data completeness
        data_completeness = analysis_data.get('confidence_score', 0.5)
        confidence += data_completeness * 0.2
        
        return min(confidence, 1.0)
    
    def _fallback_recommendation(self, student_data: Dict[str, Any], 
                               similar_students: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Fallback recommendation when AI is not available"""
        if similar_students:
            top_student = similar_students[0]
            pathway = top_student.get('target_pathway', 'General Higher Education Pathway')
            
            return {
                "recommended_pathway": pathway,
                "reasoning": f"Based on students with similar academic profiles who successfully pursued: {pathway}",
                "career_opportunities": [
                    "Industry-specific roles in your field",
                    "Graduate programs and higher studies",
                    "Research and development positions",
                    "Entrepreneurship opportunities"
                ],
                "suggested_courses": [
                    "Foundation courses in your preferred field",
                    "Advanced specialization courses",
                    "Practical skill development programs"
                ],
                "skills_to_develop": [
                    "Core subject knowledge",
                    "Problem-solving abilities",
                    "Communication skills",
                    "Technical expertise",
                    "Industry awareness"
                ],
                "additional_recommendations": "Research specific colleges and admission requirements. Consider talking to current students in similar programs."
            }
        else:
            # Generic recommendation based on preferred field
            field = student_data.get('preferred_field', 'general')
            field_pathways = {
                'Engineering': "B.Tech/B.E. in relevant branch → M.Tech/MS → Industry/Research",
                'Science': "B.Sc in chosen discipline → M.Sc → PhD/Industry",
                'Commerce': "B.Com/BBA → MBA → Professional courses (CA, CS, CMA)",
                'Arts': "BA in chosen subject → MA → PhD/Teaching/Industry",
                'Design': "B.Des → M.Des → Industry/Entrepreneurship",
                'Management': "BBA → MBA → Industry/Entrepreneurship"
            }
            
            pathway = field_pathways.get(field, "Higher Education → Specialization → Career")
            
            return {
                "recommended_pathway": pathway,
                "reasoning": f"Standard pathway for {field} field based on your preferences and academic background.",
                "career_opportunities": [
                    "Various roles in your chosen industry",
                    "Higher education and research opportunities",
                    "Government sector positions",
                    "Entrepreneurial ventures"
                ],
                "suggested_courses": [
                    "Undergraduate degree in your field",
                    "Postgraduate specialization",
                    "Professional certification courses"
                ],
                "skills_to_develop": [
                    "Academic excellence",
                    "Practical application skills",
                    "Industry knowledge",
                    "Networking abilities"
                ],
                "additional_recommendations": "Focus on building a strong academic foundation. Explore internship opportunities early in your career."
            }
    
    def _load_pathway_database(self) -> Dict[str, Any]:
        """Load pathway database for reference"""
        # This could be loaded from a file or database
        return {
            'engineering_pathways': [
                'B.Tech Computer Science → M.Tech AI → PhD Research',
                'B.E Mechanical → M.Tech Robotics → Industry',
                'B.Tech Electronics → M.Tech VLSI → Industry'
            ],
            'science_pathways': [
                'B.Sc Physics → M.Sc Astrophysics → PhD',
                'B.Sc Biology → M.Sc Biotechnology → Industry',
                'B.Sc IT → M.Sc Data Analytics → Industry'
            ],
            'commerce_pathways': [
                'B.Com → MBA Finance → Industry',
                'BBA → MBA Marketing → Industry',
                'B.Com → CA → Practice'
            ]
        }
