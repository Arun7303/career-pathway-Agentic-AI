#!/usr/bin/env python3
"""
Test script for the enhanced agentic AI system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.agentic_orchestrator import agentic_orchestrator

def test_enhanced_recommendation():
    """Test the enhanced recommendation system with Arun's profile"""
    
    # Arun's profile data
    student_data = {
        'name': 'Arun Adhikari',
        'mobile_number': '9876543210',
        'email': 'arun@example.com',
        'education_type': 'HSC',
        'ssc_percent': 70.0,
        'hsc_percent': 82.0,
        'diploma_percent': 0,
        'subjects': 'Science',
        'interests': ['Cybersecurity', 'Data Science', 'Web Development'],
        'preferred_field': 'Science',
        'preferred_mode': 'Hybrid',
        'budget': 3.0,
        'location_preference': 'Pune'
    }
    
    print("🧪 Testing Enhanced Agentic AI System")
    print("=" * 50)
    print(f"Student: {student_data['name']}")
    print(f"Interests: {', '.join(student_data['interests'])}")
    print(f"Budget: {student_data['budget']} Lakhs/year")
    print(f"Location: {student_data['location_preference']}")
    print("=" * 50)
    
    try:
        # Process the recommendation
        print("🤖 Processing recommendation through agentic AI...")
        result = agentic_orchestrator.process_student_request(student_data)
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
            return False
        
        # Display results
        print("\n✅ Recommendation generated successfully!")
        print(f"⏱️  Processing time: {result.get('processing_time', 0):.2f} seconds")
        
        recommendation = result.get('recommendation', {})
        if recommendation:
            print(f"\n🎯 Recommended Pathway:")
            print(f"   {recommendation.get('recommended_pathway', 'N/A')}")
            
            print(f"\n💡 Reasoning:")
            print(f"   {recommendation.get('reasoning', 'N/A')}")
            
            # Career opportunities
            career_ops = recommendation.get('career_opportunities', [])
            if career_ops:
                print(f"\n💼 Career Opportunities:")
                for i, opp in enumerate(career_ops[:3], 1):
                    if isinstance(opp, dict):
                        title = opp.get('title', f'Opportunity {i}')
                        description = opp.get('description', 'N/A')
                        print(f"   {i}. {title}: {description}")
                    else:
                        print(f"   {i}. {opp}")
            
            # Skills to develop
            skills = recommendation.get('skills_to_develop', [])
            if skills:
                print(f"\n🛠️  Skills to Develop:")
                for i, skill in enumerate(skills[:5], 1):
                    if isinstance(skill, dict):
                        skill_name = skill.get('skill', f'Skill {i}')
                        importance = skill.get('importance', 'Medium')
                        print(f"   {i}. {skill_name} ({importance})")
                    else:
                        print(f"   {i}. {skill}")
        
        # Analysis data
        analysis = result.get('analysis_data', {})
        if analysis:
            print(f"\n📊 Analysis Summary:")
            academic = analysis.get('academic_analysis', {})
            if academic:
                print(f"   Performance Level: {academic.get('performance_level', 'N/A')}")
                print(f"   Average Score: {academic.get('average_score', 0):.1f}%")
            
            interests = analysis.get('interest_analysis', {})
            if interests:
                print(f"   Primary Category: {interests.get('primary_category', 'N/A')}")
        
        # Validation
        validation = result.get('validation', {})
        if validation:
            print(f"\n✅ Validation:")
            print(f"   Score: {validation.get('validation_score', 0):.2f}")
            print(f"   Valid: {validation.get('is_valid', False)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🚀 Enhanced Agentic AI Course Pathway Recommender - Test")
    print("=" * 60)
    
    success = test_enhanced_recommendation()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Test completed successfully!")
        print("💡 The enhanced system is working properly.")
        print("🌐 Run 'python run.py' to start the web application")
    else:
        print("⚠️  Test failed. Please check the errors above.")
        print("💡 Make sure all dependencies are installed and configured properly.")
    
    return success

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

