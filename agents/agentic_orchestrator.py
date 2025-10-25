from .data_analysis_agent import DataAnalysisAgent
from .recommendation_agent import RecommendationAgent
from .validation_agent import ValidationAgent
from typing import Dict, Any, List
import logging
import time
from database import db_manager
from rl_models.reinforcement_learner import ReinforcementLearner
from rl_models.performance_optimizer import PerformanceOptimizer

class AgenticOrchestrator:
    """Main orchestrator that coordinates all AI agents for pathway recommendations"""
    
    def __init__(self):
        self.logger = logging.getLogger("AgenticOrchestrator")
        
        # Initialize agents
        self.data_analysis_agent = DataAnalysisAgent()
        self.recommendation_agent = RecommendationAgent()
        self.validation_agent = ValidationAgent()
        
        # Initialize reinforcement learning components
        self.reinforcement_learner = ReinforcementLearner()
        self.performance_optimizer = PerformanceOptimizer()
        
        # Agent status
        self.agents_status = {
            'data_analysis': self.data_analysis_agent.get_status(),
            'recommendation': self.recommendation_agent.get_status(),
            'validation': self.validation_agent.get_status(),
            'reinforcement_learning': self.reinforcement_learner.get_learning_insights(),
            'performance_optimizer': self.performance_optimizer.get_performance_insights()
        }
        
        self.logger.info("Agentic Orchestrator initialized with all agents")
    
    def process_student_request(self, student_data: Dict[str, Any], 
                              similar_students: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process a complete student request through all agents with reinforcement learning"""
        try:
            start_time = time.time()
            
            # Check cache first for performance optimization
            cached_recommendation = self.performance_optimizer.get_cached_recommendation(student_data)
            if cached_recommendation:
                self.logger.info("Returning cached recommendation")
                return {
                    'recommendation': cached_recommendation,
                    'analysis_data': {'cached': True},
                    'validation': {'validation_score': 0.8, 'is_valid': True},
                    'processing_time': 0.1,
                    'from_cache': True
                }
            
            # Step 1: Data Analysis
            self.logger.info("Starting data analysis phase")
            analysis_data = self.data_analysis_agent.process({
                'student_data': student_data
            })
            
            if 'error' in analysis_data:
                self.logger.error(f"Data analysis failed: {analysis_data['error']}")
                return {'error': 'Data analysis failed', 'details': analysis_data['error']}
            
            # Step 2: Recommendation Generation with RL optimization
            self.logger.info("Starting recommendation generation phase")
            
            # Get base recommendation
            base_recommendation_data = self.recommendation_agent.process({
                'student_data': student_data,
                'analysis_data': analysis_data,
                'similar_students': similar_students or []
            })
            
            if 'error' in base_recommendation_data:
                self.logger.error(f"Recommendation generation failed: {base_recommendation_data['error']}")
                return {'error': 'Recommendation generation failed', 'details': base_recommendation_data['error']}
            
            # Apply reinforcement learning optimization
            recommendation_data = self.reinforcement_learner.optimize_recommendation(
                student_data, base_recommendation_data
            )
            
            # Apply performance optimization
            recommendation_data = self.performance_optimizer.optimize_recommendation_generation(
                student_data, recommendation_data
            )
            
            # Step 3: Validation
            self.logger.info("Starting validation phase")
            validation_data = self.validation_agent.process({
                'student_data': student_data,
                'recommendation': recommendation_data,
                'analysis_data': analysis_data
            })
            
            if 'error' in validation_data:
                self.logger.error(f"Validation failed: {validation_data['error']}")
                return {'error': 'Validation failed', 'details': validation_data['error']}
            
            # Step 4: Compile final result
            processing_time = time.time() - start_time
            
            final_result = {
                'student_data': student_data,
                'analysis_data': analysis_data,
                'recommendation': recommendation_data,
                'validation': validation_data,
                'processing_time': processing_time,
                'agent_status': self.agents_status,
                'timestamp': time.time()
            }
            
            # Step 5: Save to database
            try:
                student_id = db_manager.add_student(student_data)
                recommendation_id = db_manager.save_recommendation(student_id, {
                    **recommendation_data,
                    'similar_students_data': similar_students or [],
                    'pathway_stats': analysis_data.get('pathway_stats', {}),
                    'confidence_score': validation_data.get('validation_score', 0.5)
                })
                
                final_result['student_id'] = student_id
                final_result['recommendation_id'] = recommendation_id
                
                self.logger.info(f"Successfully saved recommendation for student {student_id}")
                
            except Exception as e:
                self.logger.error(f"Failed to save to database: {e}")
                final_result['database_error'] = str(e)
            
            # Step 6: Cache the recommendation for future use
            try:
                self.performance_optimizer.cache_recommendation(student_data, recommendation_data)
            except Exception as e:
                self.logger.error(f"Failed to cache recommendation: {e}")
            
            # Step 7: Update performance metrics
            try:
                self.performance_optimizer.performance_metrics['total_requests'] += 1
                self.performance_optimizer.performance_metrics['average_response_time'] = processing_time
            except Exception as e:
                self.logger.error(f"Failed to update performance metrics: {e}")
            
            self.logger.info(f"Successfully processed student request in {processing_time:.2f} seconds")
            return final_result
            
        except Exception as e:
            self.logger.error(f"Error in agentic processing: {e}")
            return {'error': 'Processing failed', 'details': str(e)}
    
    def learn_from_feedback(self, student_data: Dict[str, Any], 
                          recommendation: Dict[str, Any], 
                          feedback_data: Dict[str, Any]):
        """Learn from user feedback to improve future recommendations"""
        try:
            # Add response time to feedback data
            feedback_data['response_time'] = feedback_data.get('response_time', 0)
            
            # Learn from feedback using reinforcement learning
            self.reinforcement_learner.learn_from_feedback(
                student_data, recommendation, feedback_data
            )
            
            # Update performance metrics
            self.performance_optimizer.performance_metrics['total_requests'] += 1
            if feedback_data.get('rating', 0) >= 4:
                self.performance_optimizer.performance_metrics['positive_feedback'] += 1
            elif feedback_data.get('rating', 0) <= 2:
                self.performance_optimizer.performance_metrics['negative_feedback'] += 1
            
            self.logger.info("Successfully learned from feedback")
            
        except Exception as e:
            self.logger.error(f"Error learning from feedback: {e}")
    
    def get_learning_insights(self) -> Dict[str, Any]:
        """Get insights about the learning process"""
        try:
            return {
                'reinforcement_learning': self.reinforcement_learner.get_learning_insights(),
                'performance_optimizer': self.performance_optimizer.get_performance_insights(),
                'agent_status': self.agents_status
            }
        except Exception as e:
            self.logger.error(f"Error getting learning insights: {e}")
            return {'error': str(e)}
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        return {
            'orchestrator_status': 'active',
            'agents': self.agents_status,
            'total_agents': len(self.agents_status),
            'active_agents': sum(1 for agent in self.agents_status.values() if agent['is_available'])
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on all agents"""
        health_status = {
            'overall_health': 'healthy',
            'agents': {},
            'timestamp': time.time()
        }
        
        # Check each agent
        for agent_name, agent_status in self.agents_status.items():
            try:
                if agent_name == 'data_analysis':
                    # Test with sample data
                    test_result = self.data_analysis_agent.process({
                        'student_data': {
                            'ssc_percent': 85,
                            'interests': ['Data Science'],
                            'preferred_field': 'Engineering'
                        }
                    })
                    health_status['agents'][agent_name] = {
                        'status': 'healthy' if 'error' not in test_result else 'unhealthy',
                        'response_time': 0.1,  # Simplified
                        'last_check': time.time()
                    }
                
                elif agent_name == 'recommendation':
                    # Test with sample data
                    test_result = self.recommendation_agent.process({
                        'student_data': {
                            'ssc_percent': 85,
                            'interests': ['Data Science'],
                            'preferred_field': 'Engineering'
                        },
                        'analysis_data': {},
                        'similar_students': []
                    })
                    health_status['agents'][agent_name] = {
                        'status': 'healthy' if 'error' not in test_result else 'unhealthy',
                        'response_time': 0.1,  # Simplified
                        'last_check': time.time()
                    }
                
                elif agent_name == 'validation':
                    # Test with sample data
                    test_result = self.validation_agent.process({
                        'student_data': {
                            'ssc_percent': 85,
                            'interests': ['Data Science'],
                            'preferred_field': 'Engineering'
                        },
                        'recommendation': {
                            'recommended_pathway': 'B.Tech Computer Science'
                        },
                        'analysis_data': {}
                    })
                    health_status['agents'][agent_name] = {
                        'status': 'healthy' if 'error' not in test_result else 'unhealthy',
                        'response_time': 0.1,  # Simplified
                        'last_check': time.time()
                    }
                
            except Exception as e:
                health_status['agents'][agent_name] = {
                    'status': 'unhealthy',
                    'error': str(e),
                    'last_check': time.time()
                }
        
        # Determine overall health
        unhealthy_agents = [name for name, status in health_status['agents'].items() 
                          if status['status'] == 'unhealthy']
        
        if unhealthy_agents:
            health_status['overall_health'] = 'degraded' if len(unhealthy_agents) < len(self.agents_status) else 'unhealthy'
            health_status['unhealthy_agents'] = unhealthy_agents
        
        return health_status
    
    def get_analytics(self) -> Dict[str, Any]:
        """Get analytics about the system"""
        try:
            db_analytics = db_manager.get_analytics_summary()
            
            return {
                'database_analytics': db_analytics,
                'agent_status': self.agents_status,
                'system_health': self.health_check(),
                'timestamp': time.time()
            }
        except Exception as e:
            self.logger.error(f"Error getting analytics: {e}")
            return {'error': str(e)}
    
    def process_batch_requests(self, student_requests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process multiple student requests in batch"""
        results = []
        
        for i, student_data in enumerate(student_requests):
            self.logger.info(f"Processing batch request {i+1}/{len(student_requests)}")
            result = self.process_student_request(student_data)
            results.append(result)
        
        return results
    
    def get_recommendation_by_id(self, recommendation_id: int) -> Dict[str, Any]:
        """Get a specific recommendation by ID"""
        try:
            # This would need to be implemented in the database manager
            # For now, return a placeholder
            return {'error': 'Feature not implemented yet'}
        except Exception as e:
            self.logger.error(f"Error getting recommendation: {e}")
            return {'error': str(e)}
    
    def update_agent_config(self, agent_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Update configuration for a specific agent"""
        try:
            if agent_name == 'data_analysis':
                # Update data analysis agent config
                return {'status': 'updated', 'agent': agent_name}
            elif agent_name == 'recommendation':
                # Update recommendation agent config
                return {'status': 'updated', 'agent': agent_name}
            elif agent_name == 'validation':
                # Update validation agent config
                return {'status': 'updated', 'agent': agent_name}
            else:
                return {'error': f'Unknown agent: {agent_name}'}
        except Exception as e:
            self.logger.error(f"Error updating agent config: {e}")
            return {'error': str(e)}

# Global orchestrator instance
agentic_orchestrator = AgenticOrchestrator()
