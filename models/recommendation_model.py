import google.generativeai as genai
import json
import re
from config import Config

class RecommendationModel:
    def __init__(self):
        self.api_key = Config.GOOGLE_API_KEY
        self.model = None
        self.is_available = False
        
        if self.api_key and self.api_key != 'your_actual_google_api_key_here':
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(Config.MODEL_NAME)
                self.is_available = True
                print("Google AI Gemini configured successfully")
            except Exception as e:
                print(f"Failed to configure Google AI: {e}")
                self.is_available = False
        else:
            print("Google API key not found. Using fallback recommendations.")
            self.is_available = False
    
    def generate_personalized_recommendation(self, student_data, similar_students, pathway_stats):
        """Generate personalized recommendation using Google AI"""
        
        if not self.is_available:
            return self._fallback_recommendation(student_data, similar_students)
        
        try:
            prompt = self._create_prompt(student_data, similar_students, pathway_stats)
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                return self._parse_ai_response(response.text)
            else:
                return self._fallback_recommendation(student_data, similar_students)
                
        except Exception as e:
            print(f"AI API Error: {e}")
            return self._fallback_recommendation(student_data, similar_students)
    
    def _create_prompt(self, student_data, similar_students, pathway_stats):
        """Create prompt for AI model"""
        
        # Format academic background
        academic_background = f"""
        - Education Type: {student_data['education_type']}
        - SSC Percentage: {student_data['ssc_percent']}%
        - HSC Percentage: {student_data.get('hsc_percent', 'N/A')}%
        - Diploma Percentage: {student_data.get('diploma_percent', 'N/A')}%
        - Subjects: {student_data['subjects']}
        """
        
        # Format preferences
        preferences = f"""
        - Interests: {', '.join(student_data['interests'])}
        - Preferred Field: {student_data['preferred_field']}
        - Preferred Mode: {student_data['preferred_mode']}
        - Budget: {student_data['budget']} Lakhs per year
        - Location Preference: {student_data['location_preference']}
        """
        
        prompt = f"""
        ROLE: You are an expert career counselor and educational pathway advisor for Indian students.

        TASK: Provide a comprehensive educational pathway recommendation based on the student's profile.

        STUDENT PROFILE:
        ACADEMIC BACKGROUND:
        {academic_background}

        PREFERENCES:
        {preferences}

        SIMILAR SUCCESSFUL STUDENTS:
        {self._format_similar_students(similar_students)}

        PATHWAY STATISTICS:
        {json.dumps(pathway_stats, indent=2) if pathway_stats else "No pathway statistics available"}

        REQUIREMENTS:
        1. Recommend a specific educational pathway (e.g., "B.Tech Computer Science → M.Tech AI → PhD Research")
        2. Explain why this pathway suits the student's profile
        3. List 3-5 career opportunities after completion
        4. Suggest 3-4 specific courses or degrees
        5. Mention 4-5 key skills to develop
        6. Provide additional practical advice

        FORMAT YOUR RESPONSE AS JSON:
        {{
            "recommended_pathway": "Detailed pathway description",
            "reasoning": "Why this pathway is suitable for this specific student",
            "career_opportunities": ["Opportunity 1", "Opportunity 2", "Opportunity 3", "Opportunity 4"],
            "suggested_courses": ["Course 1", "Course 2", "Course 3"],
            "skills_to_develop": ["Skill 1", "Skill 2", "Skill 3", "Skill 4", "Skill 5"],
            "additional_recommendations": "Practical advice about colleges, preparation, timelines, etc."
        }}

        Make the recommendation personalized, practical, and specific to the Indian education system.
        """
        
        return prompt
    
    def _format_similar_students(self, similar_students):
        """Format similar students data for the prompt"""
        if not similar_students:
            return "No similar student profiles found in our database."
            
        formatted = []
        for i, student in enumerate(similar_students[:3], 1):
            formatted.append(f"""
            Student {i} (Similarity Score: {student.get('similarity_score', 0):.2f}):
            - Successful Pathway: {student.get('target_pathway', 'N/A')}
            - Academic Scores: SSC {student.get('ssc_percent')}%, HSC {student.get('hsc_percent', 'N/A')}%, Diploma {student.get('diploma_percent', 'N/A')}%
            - Interests: {', '.join(student.get('interests_processed', []))}
            - Field: {student.get('preferred_field', 'N/A')}
            """)
        return '\n'.join(formatted)
    
    def _parse_ai_response(self, response_text):
        """Parse AI response and extract JSON"""
        try:
            # Clean the response text
            cleaned_text = response_text.strip()
            
            # Try to find JSON in the response
            json_match = re.search(r'\{.*\}', cleaned_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                recommendation_data = json.loads(json_str)
                
                # Validate required fields
                required_fields = ['recommended_pathway', 'reasoning', 'career_opportunities', 
                                 'suggested_courses', 'skills_to_develop', 'additional_recommendations']
                
                for field in required_fields:
                    if field not in recommendation_data:
                        recommendation_data[field] = f"AI recommendation - {field} not provided"
                
                return recommendation_data
            else:
                # If no JSON found, structure the text response
                return self._structure_text_response(cleaned_text)
                
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            return self._structure_text_response(response_text)
        except Exception as e:
            print(f"Error parsing AI response: {e}")
            return self._fallback_recommendation({}, [])
    
    def _structure_text_response(self, text):
        """Structure text response when JSON parsing fails"""
        # Split text into paragraphs and use them meaningfully
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
        
        return {
            "recommended_pathway": paragraphs[0] if paragraphs else "AI Recommended Pathway",
            "reasoning": paragraphs[1] if len(paragraphs) > 1 else "Personalized AI recommendation based on your profile.",
            "career_opportunities": ["Various opportunities in your chosen field", "Graduate programs", "Industry positions"],
            "suggested_courses": ["Foundation courses", "Advanced specialization", "Practical projects"],
            "skills_to_develop": ["Technical skills", "Soft skills", "Industry knowledge", "Research abilities"],
            "additional_recommendations": paragraphs[-1] if paragraphs else "Consult with academic advisors for detailed planning."
        }
    
    def _fallback_recommendation(self, student_data, similar_students):
        """Fallback recommendation when AI is unavailable"""
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