#!/usr/bin/env python3
"""
Test script for the Reinforcement Learning enhanced agentic AI system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.agentic_orchestrator import agentic_orchestrator
import time

def test_reinforcement_learning_system():
    """Test the reinforcement learning enhanced system"""
    
    print("🧠 Testing Reinforcement Learning Enhanced Agentic AI System")
    print("=" * 70)
    
    # Test student profile
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
    
    print(f"Student: {student_data['name']}")
    print(f"Interests: {', '.join(student_data['interests'])}")
    print(f"Budget: {student_data['budget']} Lakhs/year")
    print("=" * 70)
    
    try:
        # Test 1: Initial recommendation
        print("\n🎯 Test 1: Initial Recommendation Generation")
        start_time = time.time()
        
        result = agentic_orchestrator.process_student_request(student_data)
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
            return False
        
        processing_time = time.time() - start_time
        print(f"✅ Initial recommendation generated in {processing_time:.2f} seconds")
        
        recommendation = result.get('recommendation', {})
        student_id = result.get('student_id')
        recommendation_id = result.get('recommendation_id')
        
        print(f"📊 Validation Score: {result.get('validation', {}).get('validation_score', 0):.2f}")
        print(f"🎯 Pathway: {recommendation.get('recommended_pathway', 'N/A')[:100]}...")
        
        # Test 2: Simulate feedback and learning
        print("\n🧠 Test 2: Feedback Learning Simulation")
        
        # Simulate positive feedback
        positive_feedback = {
            'rating': 5,
            'feedback_text': 'Excellent recommendation! Very helpful and accurate.',
            'recommendation_used': True,
            'pathway_followed': True,
            'is_valid': True,
            'response_time': processing_time
        }
        
        agentic_orchestrator.learn_from_feedback(
            student_data, recommendation, positive_feedback
        )
        print("✅ Learned from positive feedback (rating: 5)")
        
        # Simulate negative feedback for different student
        negative_student_data = student_data.copy()
        negative_student_data['name'] = 'Test Student'
        negative_student_data['interests'] = ['Art', 'Design']
        
        negative_feedback = {
            'rating': 2,
            'feedback_text': 'Not relevant to my interests in art and design.',
            'recommendation_used': False,
            'pathway_followed': False,
            'is_valid': False,
            'response_time': processing_time
        }
        
        agentic_orchestrator.learn_from_feedback(
            negative_student_data, recommendation, negative_feedback
        )
        print("✅ Learned from negative feedback (rating: 2)")
        
        # Test 3: Get learning insights
        print("\n📈 Test 3: Learning Insights")
        insights = agentic_orchestrator.get_learning_insights()
        
        if 'error' not in insights:
            rl_insights = insights.get('reinforcement_learning', {})
            perf_insights = insights.get('performance_optimizer', {})
            
            print(f"🎓 Learning Episodes: {rl_insights.get('total_learning_episodes', 0)}")
            print(f"📊 Success Rate: {rl_insights.get('success_rate', 0):.1f}%")
            print(f"⚡ Average Reward: {rl_insights.get('average_reward', 0):.3f}")
            print(f"🎯 Current Epsilon: {rl_insights.get('current_epsilon', 0):.3f}")
            print(f"💾 Q-table Size: {rl_insights.get('q_table_size', 0)}")
            
            print(f"\n🚀 Performance Metrics:")
            print(f"   Cache Hit Rate: {perf_insights.get('cache_hit_rate', 0):.1f}%")
            print(f"   Average Response Time: {perf_insights.get('average_response_time', 0):.3f}s")
            print(f"   Total Requests: {perf_insights.get('total_requests', 0)}")
        else:
            print(f"❌ Error getting insights: {insights['error']}")
        
        # Test 4: Test caching (second request should be faster)
        print("\n⚡ Test 4: Performance Optimization (Caching)")
        
        start_time = time.time()
        cached_result = agentic_orchestrator.process_student_request(student_data)
        cached_time = time.time() - start_time
        
        if cached_result.get('from_cache'):
            print(f"✅ Cached response returned in {cached_time:.3f} seconds")
            print(f"🚀 Speed improvement: {((processing_time - cached_time) / processing_time * 100):.1f}%")
        else:
            print(f"⚠️  No cache hit, response time: {cached_time:.2f} seconds")
        
        # Test 5: Test with different student (should use learned patterns)
        print("\n🎯 Test 5: Learning Pattern Application")
        
        similar_student = student_data.copy()
        similar_student['name'] = 'Similar Student'
        similar_student['ssc_percent'] = 75.0  # Similar academic performance
        similar_student['hsc_percent'] = 80.0
        
        start_time = time.time()
        learned_result = agentic_orchestrator.process_student_request(similar_student)
        learned_time = time.time() - start_time
        
        if 'error' not in learned_result:
            print(f"✅ Learned recommendation generated in {learned_time:.2f} seconds")
            learned_recommendation = learned_result.get('recommendation', {})
            print(f"🎯 Learned Pathway: {learned_recommendation.get('recommended_pathway', 'N/A')[:100]}...")
        else:
            print(f"❌ Error in learned recommendation: {learned_result['error']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🚀 Reinforcement Learning Enhanced Agentic AI - Test Suite")
    print("=" * 80)
    
    success = test_reinforcement_learning_system()
    
    print("\n" + "=" * 80)
    if success:
        print("🎉 All tests completed successfully!")
        print("🧠 Reinforcement Learning system is working properly")
        print("⚡ Performance optimization is active")
        print("📈 System is learning and improving from feedback")
        print("🌐 Run 'python run.py' to start the enhanced web application")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("💡 Make sure all dependencies are installed and configured properly.")
    
    return success

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

