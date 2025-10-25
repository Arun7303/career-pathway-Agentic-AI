from .base_agent import BaseAgent
from typing import Dict, Any, List
import re
import json

class ValidationAgent(BaseAgent):
    """Agent responsible for validating recommendations and ensuring quality"""
    
    def __init__(self):
        super().__init__("ValidationAgent")
        self.validation_rules = self._load_validation_rules()
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate recommendation and return validation results"""
        try:
            student_data = data.get('student_data', {})
            recommendation = data.get('recommendation', {})
            analysis_data = data.get('analysis_data', {})
            
            # Perform various validations
            academic_validation = self._validate_academic_fit(student_data, recommendation)
            budget_validation = self._validate_budget_constraints(student_data, recommendation)
            interest_validation = self._validate_interest_alignment(student_data, recommendation)
            feasibility_validation = self._validate_feasibility(student_data, recommendation)
            ai_validation = self._validate_with_ai(student_data, recommendation, analysis_data)
            
            # Calculate overall validation score
            validation_score = self._calculate_validation_score([
                academic_validation, budget_validation, interest_validation, 
                feasibility_validation, ai_validation
            ])
            
            # Generate validation report
            validation_report = self._generate_validation_report(
                academic_validation, budget_validation, interest_validation,
                feasibility_validation, ai_validation, validation_score
            )
            
            return {
                'validation_score': validation_score,
                'validation_report': validation_report,
                'is_valid': validation_score >= 0.7,
                'recommendations': self._generate_improvement_recommendations(
                    academic_validation, budget_validation, interest_validation,
                    feasibility_validation, ai_validation
                )
            }
            
        except Exception as e:
            self.logger.error(f"Error in validation: {e}")
            return {'error': str(e), 'validation_score': 0.0, 'is_valid': False}
    
    def _validate_academic_fit(self, student_data: Dict[str, Any], 
                             recommendation: Dict[str, Any]) -> Dict[str, Any]:
        """Validate if recommendation fits student's academic capabilities"""
        ssc_percent = student_data.get('ssc_percent', 0)
        hsc_percent = student_data.get('hsc_percent', 0)
        diploma_percent = student_data.get('diploma_percent', 0)
        
        # Calculate average academic performance
        scores = [score for score in [ssc_percent, hsc_percent, diploma_percent] if score > 0]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        # Analyze pathway complexity
        pathway = recommendation.get('recommended_pathway', '')
        complexity_score = self._assess_pathway_complexity(pathway)
        
        # Determine academic fit
        if avg_score >= 85 and complexity_score >= 0.8:
            fit_score = 1.0
            status = "Excellent fit"
        elif avg_score >= 75 and complexity_score >= 0.6:
            fit_score = 0.8
            status = "Good fit"
        elif avg_score >= 65 and complexity_score >= 0.4:
            fit_score = 0.6
            status = "Moderate fit"
        elif avg_score >= 55 and complexity_score >= 0.2:
            fit_score = 0.4
            status = "Challenging but achievable"
        else:
            fit_score = 0.2
            status = "May be too challenging"
        
        return {
            'fit_score': fit_score,
            'status': status,
            'average_score': avg_score,
            'pathway_complexity': complexity_score,
            'concerns': self._identify_academic_concerns(avg_score, complexity_score)
        }
    
    def _validate_budget_constraints(self, student_data: Dict[str, Any], 
                                   recommendation: Dict[str, Any]) -> Dict[str, Any]:
        """Validate if recommendation fits student's budget"""
        student_budget = student_data.get('budget', 0)
        
        # Estimate pathway cost (simplified)
        pathway = recommendation.get('recommended_pathway', '')
        estimated_cost = self._estimate_pathway_cost(pathway)
        
        # Calculate affordability
        if student_budget >= estimated_cost * 1.2:
            affordability_score = 1.0
            status = "Fully affordable"
        elif student_budget >= estimated_cost:
            affordability_score = 0.8
            status = "Affordable with careful planning"
        elif student_budget >= estimated_cost * 0.7:
            affordability_score = 0.6
            status = "Challenging but possible with financial aid"
        elif student_budget >= estimated_cost * 0.5:
            affordability_score = 0.4
            status = "Requires significant financial assistance"
        else:
            affordability_score = 0.2
            status = "Not affordable without major financial support"
        
        return {
            'affordability_score': affordability_score,
            'status': status,
            'student_budget': student_budget,
            'estimated_cost': estimated_cost,
            'funding_gap': max(0, estimated_cost - student_budget),
            'suggestions': self._suggest_funding_options(student_budget, estimated_cost)
        }
    
    def _validate_interest_alignment(self, student_data: Dict[str, Any], 
                                   recommendation: Dict[str, Any]) -> Dict[str, Any]:
        """Validate if recommendation aligns with student's interests"""
        student_interests = student_data.get('interests', [])
        pathway = recommendation.get('recommended_pathway', '')
        career_opportunities = recommendation.get('career_opportunities', [])
        
        # Calculate interest alignment
        alignment_score = self._calculate_interest_alignment(student_interests, pathway, career_opportunities)
        
        if alignment_score >= 0.8:
            status = "Highly aligned with interests"
        elif alignment_score >= 0.6:
            status = "Well aligned with interests"
        elif alignment_score >= 0.4:
            status = "Moderately aligned with interests"
        else:
            status = "Limited alignment with interests"
        
        return {
            'alignment_score': alignment_score,
            'status': status,
            'matched_interests': self._find_matched_interests(student_interests, pathway),
            'unmatched_interests': self._find_unmatched_interests(student_interests, pathway),
            'suggestions': self._suggest_interest_improvements(student_interests, pathway)
        }
    
    def _validate_feasibility(self, student_data: Dict[str, Any], 
                            recommendation: Dict[str, Any]) -> Dict[str, Any]:
        """Validate if recommendation is feasible given constraints"""
        location = student_data.get('location_preference', '')
        preferred_mode = student_data.get('preferred_mode', '')
        pathway = recommendation.get('recommended_pathway', '')
        
        # Check location feasibility
        location_feasibility = self._check_location_feasibility(location, pathway)
        
        # Check mode feasibility
        mode_feasibility = self._check_mode_feasibility(preferred_mode, pathway)
        
        # Check timeline feasibility
        timeline_feasibility = self._check_timeline_feasibility(pathway)
        
        # Calculate overall feasibility
        feasibility_score = (location_feasibility + mode_feasibility + timeline_feasibility) / 3
        
        if feasibility_score >= 0.8:
            status = "Highly feasible"
        elif feasibility_score >= 0.6:
            status = "Feasible with some adjustments"
        elif feasibility_score >= 0.4:
            status = "Challenging but possible"
        else:
            status = "May not be feasible"
        
        return {
            'feasibility_score': feasibility_score,
            'status': status,
            'location_feasibility': location_feasibility,
            'mode_feasibility': mode_feasibility,
            'timeline_feasibility': timeline_feasibility,
            'constraints': self._identify_feasibility_constraints(location, preferred_mode, pathway)
        }
    
    def _validate_with_ai(self, student_data: Dict[str, Any], 
                         recommendation: Dict[str, Any], 
                         analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use AI to validate the recommendation"""
        if not self.is_available:
            return {'ai_score': 0.5, 'status': 'AI validation not available'}
        
        prompt = f"""
        ROLE: You are an expert educational counselor validating a pathway recommendation.

        STUDENT PROFILE:
        - Academic Performance: {analysis_data.get('academic_analysis', {}).get('performance_level', 'Unknown')}
        - Interests: {', '.join(student_data.get('interests', []))}
        - Preferred Field: {student_data.get('preferred_field', '')}
        - Budget: {student_data.get('budget', 0)} Lakhs
        - Location: {student_data.get('location_preference', '')}
        - Learning Mode: {student_data.get('preferred_mode', '')}

        RECOMMENDED PATHWAY:
        {recommendation.get('recommended_pathway', '')}

        TASK: Validate this recommendation and provide a score (0-1) and detailed analysis.

        CONSIDER:
        1. Academic fit and capability match
        2. Interest alignment
        3. Budget feasibility
        4. Location and mode constraints
        5. Market demand and career prospects
        6. Timeline and milestone achievability

        FORMAT YOUR RESPONSE AS JSON:
        {{
            "validation_score": 0.0-1.0,
            "overall_assessment": "Detailed assessment of the recommendation",
            "strengths": ["Strength 1", "Strength 2", "Strength 3"],
            "concerns": ["Concern 1", "Concern 2", "Concern 3"],
            "improvement_suggestions": ["Suggestion 1", "Suggestion 2"],
            "alternative_considerations": ["Alternative 1", "Alternative 2"]
        }}
        """
        
        response = self.generate_response(prompt)
        if response:
            parsed_response = self.parse_json_response(response)
            if parsed_response:
                return {
                    'ai_score': parsed_response.get('validation_score', 0.5),
                    'status': parsed_response.get('overall_assessment', 'AI validation completed'),
                    'strengths': parsed_response.get('strengths', []),
                    'concerns': parsed_response.get('concerns', []),
                    'improvement_suggestions': parsed_response.get('improvement_suggestions', []),
                    'alternatives': parsed_response.get('alternative_considerations', [])
                }
        
        return {'ai_score': 0.5, 'status': 'AI validation failed'}
    
    def _assess_pathway_complexity(self, pathway: str) -> float:
        """Assess the complexity of a pathway (0-1 scale)"""
        complexity_indicators = {
            'PhD': 1.0,
            'M.Tech': 0.9,
            'MBA': 0.8,
            'M.Sc': 0.7,
            'M.Des': 0.7,
            'B.Tech': 0.6,
            'B.E': 0.6,
            'B.Sc': 0.5,
            'B.Com': 0.4,
            'BBA': 0.4,
            'BA': 0.3,
            'Diploma': 0.3
        }
        
        max_complexity = 0.0
        for indicator, complexity in complexity_indicators.items():
            if indicator.lower() in pathway.lower():
                max_complexity = max(max_complexity, complexity)
        
        return max_complexity if max_complexity > 0 else 0.5
    
    def _estimate_pathway_cost(self, pathway: str) -> float:
        """Estimate the cost of a pathway in lakhs per year"""
        cost_indicators = {
            'PhD': 8.0,
            'M.Tech': 6.0,
            'MBA': 10.0,
            'M.Sc': 4.0,
            'M.Des': 7.0,
            'B.Tech': 5.0,
            'B.E': 5.0,
            'B.Sc': 3.0,
            'B.Com': 2.0,
            'BBA': 3.0,
            'BA': 2.0,
            'Diploma': 2.0
        }
        
        max_cost = 0.0
        for indicator, cost in cost_indicators.items():
            if indicator.lower() in pathway.lower():
                max_cost = max(max_cost, cost)
        
        return max_cost if max_cost > 0 else 3.0  # Default cost
    
    def _calculate_interest_alignment(self, interests: List[str], 
                                    pathway: str, 
                                    career_opportunities: List[str]) -> float:
        """Calculate how well interests align with pathway and career opportunities"""
        if not interests:
            return 0.5
        
        # Define interest-pathway mappings
        interest_mappings = {
            'Data Science': ['data', 'analytics', 'statistics', 'machine learning'],
            'AI': ['artificial intelligence', 'machine learning', 'deep learning', 'neural networks'],
            'Cybersecurity': ['security', 'cybersecurity', 'information security', 'network security'],
            'Web Development': ['web', 'development', 'programming', 'software'],
            'Robotics': ['robotics', 'automation', 'mechanical', 'engineering'],
            'Design': ['design', 'creative', 'visual', 'graphic'],
            'UX': ['user experience', 'ux', 'interface', 'usability'],
            'Marketing': ['marketing', 'advertising', 'branding', 'promotion'],
            'Management': ['management', 'leadership', 'business', 'administration'],
            'Research': ['research', 'analysis', 'study', 'investigation'],
            'Finance': ['finance', 'banking', 'investment', 'accounting'],
            'Psychology': ['psychology', 'behavioral', 'mental health', 'counseling']
        }
        
        total_alignment = 0.0
        for interest in interests:
            interest_keywords = interest_mappings.get(interest, [interest.lower()])
            pathway_lower = pathway.lower()
            # Handle both string and dict career opportunities
            career_texts = []
            for opp in career_opportunities:
                if isinstance(opp, dict):
                    career_texts.append(opp.get('title', str(opp)))
                else:
                    career_texts.append(str(opp))
            career_text = ' '.join(career_texts).lower()
            
            # Check alignment with pathway
            pathway_alignment = sum(1 for keyword in interest_keywords if keyword in pathway_lower)
            career_alignment = sum(1 for keyword in interest_keywords if keyword in career_text)
            
            total_alignment += (pathway_alignment + career_alignment) / (len(interest_keywords) * 2)
        
        return min(total_alignment / len(interests), 1.0)
    
    def _find_matched_interests(self, interests: List[str], pathway: str) -> List[str]:
        """Find interests that match the pathway"""
        matched = []
        pathway_lower = pathway.lower()
        
        for interest in interests:
            if interest.lower() in pathway_lower:
                matched.append(interest)
        
        return matched
    
    def _find_unmatched_interests(self, interests: List[str], pathway: str) -> List[str]:
        """Find interests that don't match the pathway"""
        matched = self._find_matched_interests(interests, pathway)
        return [interest for interest in interests if interest not in matched]
    
    def _check_location_feasibility(self, location: str, pathway: str) -> float:
        """Check if pathway is feasible from the given location"""
        # Simplified feasibility check
        major_cities = ['mumbai', 'delhi', 'bangalore', 'kolkata', 'chennai', 'pune']
        
        if location.lower() in major_cities:
            return 1.0  # High feasibility in major cities
        elif location.lower() in ['nashik', 'hyderabad', 'ahmedabad']:
            return 0.8  # Good feasibility in tier-2 cities
        else:
            return 0.6  # Moderate feasibility in other locations
    
    def _check_mode_feasibility(self, preferred_mode: str, pathway: str) -> float:
        """Check if pathway is feasible with preferred learning mode"""
        # Most pathways can be adapted to different modes
        if preferred_mode.lower() == 'hybrid':
            return 1.0
        elif preferred_mode.lower() == 'online':
            return 0.8  # Some programs may not be fully online
        else:  # offline
            return 0.9  # Most programs are available offline
    
    def _check_timeline_feasibility(self, pathway: str) -> float:
        """Check if pathway timeline is feasible"""
        # Simplified timeline check
        if 'PhD' in pathway:
            return 0.7  # Longer timeline
        elif 'M.Tech' in pathway or 'MBA' in pathway:
            return 0.8  # Medium timeline
        else:
            return 0.9  # Shorter timeline
    
    def _calculate_validation_score(self, validations: List[Dict[str, Any]]) -> float:
        """Calculate overall validation score"""
        scores = []
        for validation in validations:
            if 'fit_score' in validation:
                scores.append(validation['fit_score'])
            elif 'affordability_score' in validation:
                scores.append(validation['affordability_score'])
            elif 'alignment_score' in validation:
                scores.append(validation['alignment_score'])
            elif 'feasibility_score' in validation:
                scores.append(validation['feasibility_score'])
            elif 'ai_score' in validation:
                scores.append(validation['ai_score'])
        
        return sum(scores) / len(scores) if scores else 0.5
    
    def _generate_validation_report(self, academic_val: Dict[str, Any], 
                                  budget_val: Dict[str, Any], 
                                  interest_val: Dict[str, Any], 
                                  feasibility_val: Dict[str, Any], 
                                  ai_val: Dict[str, Any], 
                                  overall_score: float) -> str:
        """Generate comprehensive validation report"""
        report = f"""
        VALIDATION REPORT
        =================
        
        Overall Validation Score: {overall_score:.2f}/1.0
        
        Academic Fit: {academic_val.get('status', 'Not assessed')} (Score: {academic_val.get('fit_score', 0):.2f})
        Budget Feasibility: {budget_val.get('status', 'Not assessed')} (Score: {budget_val.get('affordability_score', 0):.2f})
        Interest Alignment: {interest_val.get('status', 'Not assessed')} (Score: {interest_val.get('alignment_score', 0):.2f})
        General Feasibility: {feasibility_val.get('status', 'Not assessed')} (Score: {feasibility_val.get('feasibility_score', 0):.2f})
        AI Assessment: {ai_val.get('status', 'Not assessed')} (Score: {ai_val.get('ai_score', 0):.2f})
        
        Recommendation: {'APPROVED' if overall_score >= 0.7 else 'NEEDS REVIEW'}
        """
        
        return report
    
    def _generate_improvement_recommendations(self, academic_val: Dict[str, Any], 
                                            budget_val: Dict[str, Any], 
                                            interest_val: Dict[str, Any], 
                                            feasibility_val: Dict[str, Any], 
                                            ai_val: Dict[str, Any]) -> List[str]:
        """Generate recommendations for improvement"""
        recommendations = []
        
        if academic_val.get('fit_score', 1) < 0.7:
            recommendations.append("Consider strengthening academic foundation before pursuing this pathway")
        
        if budget_val.get('affordability_score', 1) < 0.7:
            recommendations.append("Explore scholarship opportunities and financial aid options")
        
        if interest_val.get('alignment_score', 1) < 0.7:
            recommendations.append("Consider pathways that better align with your interests")
        
        if feasibility_val.get('feasibility_score', 1) < 0.7:
            recommendations.append("Review location and mode constraints for better feasibility")
        
        if ai_val.get('ai_score', 1) < 0.7:
            recommendations.extend(ai_val.get('improvement_suggestions', []))
        
        return recommendations
    
    def _identify_academic_concerns(self, avg_score: float, complexity: float) -> List[str]:
        """Identify academic concerns"""
        concerns = []
        if avg_score < 70 and complexity > 0.7:
            concerns.append("Academic performance may not be sufficient for this complex pathway")
        if avg_score < 60:
            concerns.append("Consider foundation courses to improve academic readiness")
        return concerns
    
    def _suggest_funding_options(self, student_budget: float, estimated_cost: float) -> List[str]:
        """Suggest funding options"""
        suggestions = []
        if student_budget < estimated_cost:
            suggestions.append("Apply for educational loans")
            suggestions.append("Look for scholarship opportunities")
            suggestions.append("Consider part-time work or internships")
        return suggestions
    
    def _suggest_interest_improvements(self, interests: List[str], pathway: str) -> List[str]:
        """Suggest improvements for interest alignment"""
        suggestions = []
        unmatched = self._find_unmatched_interests(interests, pathway)
        if unmatched:
            suggestions.append(f"Consider how to incorporate {', '.join(unmatched)} into your career path")
        return suggestions
    
    def _identify_feasibility_constraints(self, location: str, mode: str, pathway: str) -> List[str]:
        """Identify feasibility constraints"""
        constraints = []
        if location.lower() not in ['mumbai', 'delhi', 'bangalore', 'kolkata', 'chennai', 'pune']:
            constraints.append("Limited access to premium institutions in your location")
        if mode.lower() == 'online' and 'practical' in pathway.lower():
            constraints.append("Some practical components may require offline attendance")
        return constraints
    
    def _load_validation_rules(self) -> Dict[str, Any]:
        """Load validation rules"""
        return {
            'minimum_academic_score': 50,
            'maximum_pathway_duration': 10,  # years
            'minimum_budget_ratio': 0.5,
            'required_interest_alignment': 0.3
        }
