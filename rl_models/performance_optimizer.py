"""
Performance Optimizer for the Agentic AI System
Implements caching, response optimization, and efficiency improvements
"""

import time
import hashlib
import json
import sqlite3
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, deque
import logging
from datetime import datetime, timedelta
import threading
import queue

class PerformanceOptimizer:
    """
    Optimizes system performance through caching, prediction, and efficiency improvements
    """
    
    def __init__(self, db_path: str = "student_pathway.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        
        # Caching system
        self.recommendation_cache = {}
        self.analysis_cache = {}
        self.similar_students_cache = {}
        self.cache_ttl = 3600  # 1 hour
        
        # Performance metrics
        self.performance_metrics = {
            'total_requests': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'average_response_time': 0.0,
            'optimization_savings': 0.0
        }
        
        # Response time tracking
        self.response_times = deque(maxlen=1000)
        
        # Background optimization
        self.optimization_queue = queue.Queue()
        self.background_thread = threading.Thread(target=self._background_optimizer, daemon=True)
        self.background_thread.start()
        
        # Precomputed patterns
        self.common_patterns = self._load_common_patterns()
        
    def get_cache_key(self, student_data: Dict[str, Any]) -> str:
        """Generate cache key for student data"""
        try:
            # Create a normalized version of student data for caching
            normalized_data = {
                'education_type': student_data.get('education_type', ''),
                'ssc_percent': round(student_data.get('ssc_percent', 0), 1),
                'hsc_percent': round(student_data.get('hsc_percent', 0), 1),
                'interests': sorted(student_data.get('interests', [])),
                'preferred_field': student_data.get('preferred_field', ''),
                'budget': round(student_data.get('budget', 0), 1),
                'location_preference': student_data.get('location_preference', '')
            }
            
            # Create hash of normalized data
            data_str = json.dumps(normalized_data, sort_keys=True)
            return hashlib.md5(data_str.encode()).hexdigest()
            
        except Exception as e:
            self.logger.error(f"Error generating cache key: {e}")
            return str(hash(str(student_data)))
    
    def get_cached_recommendation(self, student_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get cached recommendation if available"""
        try:
            cache_key = self.get_cache_key(student_data)
            
            if cache_key in self.recommendation_cache:
                cached_data = self.recommendation_cache[cache_key]
                
                # Check if cache is still valid
                if time.time() - cached_data['timestamp'] < self.cache_ttl:
                    self.performance_metrics['cache_hits'] += 1
                    self.logger.info(f"Cache hit for recommendation: {cache_key[:8]}...")
                    return cached_data['recommendation']
                else:
                    # Remove expired cache
                    del self.recommendation_cache[cache_key]
            
            self.performance_metrics['cache_misses'] += 1
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting cached recommendation: {e}")
            return None
    
    def cache_recommendation(self, student_data: Dict[str, Any], recommendation: Dict[str, Any]):
        """Cache recommendation for future use"""
        try:
            cache_key = self.get_cache_key(student_data)
            
            self.recommendation_cache[cache_key] = {
                'recommendation': recommendation,
                'timestamp': time.time(),
                'student_profile': self._get_profile_summary(student_data)
            }
            
            # Limit cache size
            if len(self.recommendation_cache) > 1000:
                self._cleanup_cache()
            
            self.logger.info(f"Cached recommendation: {cache_key[:8]}...")
            
        except Exception as e:
            self.logger.error(f"Error caching recommendation: {e}")
    
    def optimize_recommendation_generation(self, student_data: Dict[str, Any], 
                                        base_recommendation: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize recommendation generation using learned patterns"""
        try:
            start_time = time.time()
            
            # Check for similar patterns
            similar_pattern = self._find_similar_pattern(student_data)
            if similar_pattern:
                optimized_recommendation = self._apply_pattern_optimization(
                    base_recommendation, similar_pattern
                )
            else:
                optimized_recommendation = base_recommendation
            
            # Apply performance optimizations
            optimized_recommendation = self._apply_performance_optimizations(
                optimized_recommendation, student_data
            )
            
            # Track performance
            response_time = time.time() - start_time
            self.response_times.append(response_time)
            self.performance_metrics['average_response_time'] = np.mean(list(self.response_times))
            
            return optimized_recommendation
            
        except Exception as e:
            self.logger.error(f"Error optimizing recommendation: {e}")
            return base_recommendation
    
    def predict_user_preferences(self, student_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict user preferences based on similar students"""
        try:
            # Get similar students from database
            similar_students = self._get_similar_students(student_data)
            
            if not similar_students:
                return {}
            
            # Analyze patterns in similar students
            preferences = {
                'preferred_pathway_types': defaultdict(int),
                'preferred_institutions': defaultdict(int),
                'preferred_careers': defaultdict(int),
                'success_factors': defaultdict(int)
            }
            
            for student in similar_students:
                # Analyze their successful pathways
                pathway = student.get('target_pathway', '')
                if pathway:
                    preferences['preferred_pathway_types'][pathway] += 1
                
                # Analyze their career choices
                career = student.get('career_choice', '')
                if career:
                    preferences['preferred_careers'][career] += 1
            
            # Convert to sorted lists
            for key in preferences:
                preferences[key] = dict(sorted(
                    preferences[key].items(), 
                    key=lambda x: x[1], 
                    reverse=True
                )[:5])  # Top 5 preferences
            
            return preferences
            
        except Exception as e:
            self.logger.error(f"Error predicting user preferences: {e}")
            return {}
    
    def optimize_ai_prompts(self, base_prompt: str, student_data: Dict[str, Any]) -> str:
        """Optimize AI prompts for better performance"""
        try:
            # Add performance hints to prompt
            performance_hints = self._get_performance_hints(student_data)
            
            optimized_prompt = f"""
            {base_prompt}
            
            PERFORMANCE OPTIMIZATION HINTS:
            - Focus on the most relevant aspects for this student profile
            - Prioritize recommendations that have shown success for similar students
            - Consider the student's budget constraints and location preferences
            - Provide specific, actionable advice rather than generic recommendations
            
            STUDENT-SPECIFIC INSIGHTS:
            {json.dumps(performance_hints, indent=2)}
            """
            
            return optimized_prompt
            
        except Exception as e:
            self.logger.error(f"Error optimizing AI prompts: {e}")
            return base_prompt
    
    def get_performance_insights(self) -> Dict[str, Any]:
        """Get performance insights and optimization recommendations"""
        try:
            total_requests = self.performance_metrics['total_requests']
            cache_hits = self.performance_metrics['cache_hits']
            cache_misses = self.performance_metrics['cache_misses']
            
            cache_hit_rate = (cache_hits / (cache_hits + cache_misses) * 100) if (cache_hits + cache_misses) > 0 else 0
            
            avg_response_time = self.performance_metrics['average_response_time']
            
            # Performance recommendations
            recommendations = []
            if cache_hit_rate < 30:
                recommendations.append("Consider increasing cache TTL or improving cache key generation")
            if avg_response_time > 10:
                recommendations.append("Response time is high, consider optimizing AI prompts or adding more caching")
            if len(self.recommendation_cache) > 800:
                recommendations.append("Cache size is large, consider implementing cache eviction policy")
            
            return {
                "cache_hit_rate": round(cache_hit_rate, 2),
                "average_response_time": round(avg_response_time, 3),
                "total_requests": total_requests,
                "cache_size": len(self.recommendation_cache),
                "performance_recommendations": recommendations,
                "optimization_savings": self.performance_metrics['optimization_savings']
            }
            
        except Exception as e:
            self.logger.error(f"Error getting performance insights: {e}")
            return {"error": str(e)}
    
    def _background_optimizer(self):
        """Background thread for continuous optimization"""
        while True:
            try:
                # Process optimization tasks
                if not self.optimization_queue.empty():
                    task = self.optimization_queue.get_nowait()
                    self._process_optimization_task(task)
                
                # Periodic cache cleanup
                if len(self.recommendation_cache) > 500:
                    self._cleanup_cache()
                
                # Update common patterns
                if len(self.response_times) % 100 == 0:
                    self._update_common_patterns()
                
                time.sleep(60)  # Run every minute
                
            except Exception as e:
                self.logger.error(f"Error in background optimizer: {e}")
                time.sleep(60)
    
    def _find_similar_pattern(self, student_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find similar patterns in the database"""
        try:
            # This is a simplified implementation
            # In a real system, this would use more sophisticated pattern matching
            
            academic_level = student_data.get('ssc_percent', 0) + student_data.get('hsc_percent', 0)
            interests = set(student_data.get('interests', []))
            
            for pattern in self.common_patterns:
                pattern_interests = set(pattern.get('common_interests', []))
                if len(interests.intersection(pattern_interests)) >= 2:
                    return pattern
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error finding similar pattern: {e}")
            return None
    
    def _apply_pattern_optimization(self, recommendation: Dict[str, Any], pattern: Dict[str, Any]) -> Dict[str, Any]:
        """Apply pattern-based optimizations"""
        try:
            optimized = recommendation.copy()
            
            # Apply pattern insights
            if pattern.get('successful_pathway'):
                optimized['recommended_pathway'] = pattern['successful_pathway']
            
            if pattern.get('common_careers'):
                optimized['career_opportunities'] = pattern['common_careers'][:3]
            
            return optimized
            
        except Exception as e:
            self.logger.error(f"Error applying pattern optimization: {e}")
            return recommendation
    
    def _apply_performance_optimizations(self, recommendation: Dict[str, Any], student_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply performance optimizations to recommendation"""
        try:
            optimized = recommendation.copy()
            
            # Optimize career opportunities (limit to top 3)
            if 'career_opportunities' in optimized:
                optimized['career_opportunities'] = optimized['career_opportunities'][:3]
            
            # Optimize skills list (limit to top 5)
            if 'skills_to_develop' in optimized:
                optimized['skills_to_develop'] = optimized['skills_to_develop'][:5]
            
            # Add performance metadata
            optimized['_performance_metadata'] = {
                'optimized': True,
                'timestamp': datetime.now().isoformat(),
                'cache_key': self.get_cache_key(student_data)
            }
            
            return optimized
            
        except Exception as e:
            self.logger.error(f"Error applying performance optimizations: {e}")
            return recommendation
    
    def _get_similar_students(self, student_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get similar students from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Simple similarity query (can be improved)
            ssc_percent = student_data.get('ssc_percent', 0)
            hsc_percent = student_data.get('hsc_percent', 0)
            interests = student_data.get('interests', [])
            
            # Find students with similar academic performance
            cursor.execute("""
                SELECT * FROM students 
                WHERE ABS(ssc_percent - ?) < 10 
                AND ABS(hsc_percent - ?) < 10
                LIMIT 10
            """, (ssc_percent, hsc_percent))
            
            similar_students = []
            for row in cursor.fetchall():
                student = dict(zip([col[0] for col in cursor.description], row))
                similar_students.append(student)
            
            conn.close()
            return similar_students
            
        except Exception as e:
            self.logger.error(f"Error getting similar students: {e}")
            return []
    
    def _get_performance_hints(self, student_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get performance hints for the student"""
        try:
            hints = {
                'academic_strength': 'Good' if student_data.get('ssc_percent', 0) > 70 else 'Average',
                'interest_diversity': len(student_data.get('interests', [])),
                'budget_category': 'High' if student_data.get('budget', 0) > 5 else 'Medium' if student_data.get('budget', 0) > 2 else 'Low',
                'location_tier': 'Tier 1' if student_data.get('location_preference', '').lower() in ['mumbai', 'delhi', 'bangalore'] else 'Other'
            }
            
            return hints
            
        except Exception as e:
            self.logger.error(f"Error getting performance hints: {e}")
            return {}
    
    def _get_profile_summary(self, student_data: Dict[str, Any]) -> str:
        """Get a summary of the student profile for caching"""
        try:
            return f"{student_data.get('education_type', '')}_{student_data.get('preferred_field', '')}_{len(student_data.get('interests', []))}"
        except Exception as e:
            self.logger.error(f"Error getting profile summary: {e}")
            return "unknown"
    
    def _cleanup_cache(self):
        """Clean up expired cache entries"""
        try:
            current_time = time.time()
            expired_keys = []
            
            for key, data in self.recommendation_cache.items():
                if current_time - data['timestamp'] > self.cache_ttl:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.recommendation_cache[key]
            
            self.logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
            
        except Exception as e:
            self.logger.error(f"Error cleaning up cache: {e}")
    
    def _load_common_patterns(self) -> List[Dict[str, Any]]:
        """Load common patterns from database"""
        try:
            # This would load patterns from a patterns table
            # For now, return some example patterns
            return [
                {
                    'common_interests': ['programming', 'web development'],
                    'successful_pathway': 'B.Tech Computer Science → M.Tech → Industry',
                    'common_careers': ['Software Engineer', 'Web Developer', 'Full Stack Developer']
                },
                {
                    'common_interests': ['data science', 'analytics'],
                    'successful_pathway': 'B.Sc Statistics → M.Sc Data Science → Industry',
                    'common_careers': ['Data Scientist', 'Data Analyst', 'Business Analyst']
                }
            ]
        except Exception as e:
            self.logger.error(f"Error loading common patterns: {e}")
            return []
    
    def _update_common_patterns(self):
        """Update common patterns based on recent data"""
        try:
            # This would analyze recent successful recommendations
            # and update the common patterns
            pass
        except Exception as e:
            self.logger.error(f"Error updating common patterns: {e}")
    
    def _process_optimization_task(self, task: Dict[str, Any]):
        """Process optimization task in background"""
        try:
            task_type = task.get('type')
            if task_type == 'cache_cleanup':
                self._cleanup_cache()
            elif task_type == 'pattern_update':
                self._update_common_patterns()
            # Add more task types as needed
            
        except Exception as e:
            self.logger.error(f"Error processing optimization task: {e}")

# Import numpy for mean calculation
import numpy as np
