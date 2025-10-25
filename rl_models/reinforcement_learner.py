"""
Reinforcement Learning Model for Course Pathway Recommendations
This model learns from user feedback and improves recommendations over time
"""

import numpy as np
import pandas as pd
import pickle
import json
import os
from typing import Dict, List, Any, Tuple, Optional
from collections import defaultdict, deque
import logging
from datetime import datetime, timedelta
import sqlite3

class ReinforcementLearner:
    """
    Reinforcement Learning model that learns from user feedback
    to improve recommendation quality and efficiency
    """
    
    def __init__(self, db_path: str = "student_pathway.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        
        # Q-Learning parameters
        self.learning_rate = 0.1
        self.discount_factor = 0.95
        self.epsilon = 0.1  # Exploration rate
        self.epsilon_decay = 0.995
        self.epsilon_min = 0.01
        
        # State and action spaces
        self.state_features = [
            'academic_performance', 'interest_category', 'budget_level',
            'location_preference', 'preferred_field', 'learning_style'
        ]
        
        self.action_space = [
            'pathway_type', 'institution_type', 'course_duration',
            'skill_focus', 'career_orientation', 'learning_mode'
        ]
        
        # Q-table and experience replay
        self.q_table = defaultdict(lambda: defaultdict(float))
        self.experience_replay = deque(maxlen=10000)
        self.reward_history = deque(maxlen=1000)
        
        # Performance metrics
        self.performance_metrics = {
            'total_recommendations': 0,
            'positive_feedback': 0,
            'negative_feedback': 0,
            'average_response_time': 0.0,
            'learning_episodes': 0
        }
        
        # Load existing model if available
        self.model_path = "rl_model.pkl"
        self.load_model()
        
    def get_state_representation(self, student_data: Dict[str, Any]) -> str:
        """Convert student data to state representation"""
        try:
            # Academic performance (0-3 scale)
            ssc = student_data.get('ssc_percent', 0)
            hsc = student_data.get('hsc_percent', 0)
            avg_score = (ssc + hsc) / 2 if hsc > 0 else ssc
            academic_perf = min(3, int(avg_score / 25))  # 0-3 scale
            
            # Interest category
            interests = student_data.get('interests', [])
            interest_cat = self._categorize_interests(interests)
            
            # Budget level (0-3 scale)
            budget = student_data.get('budget', 0)
            budget_level = min(3, int(budget / 2))  # 0-3 scale
            
            # Location preference
            location = student_data.get('location_preference', 'unknown')
            location_code = self._encode_location(location)
            
            # Preferred field
            field = student_data.get('preferred_field', 'general')
            field_code = self._encode_field(field)
            
            # Learning style (inferred from preferences)
            mode = student_data.get('preferred_mode', 'hybrid')
            learning_style = self._encode_learning_style(mode)
            
            state = f"{academic_perf}_{interest_cat}_{budget_level}_{location_code}_{field_code}_{learning_style}"
            return state
            
        except Exception as e:
            self.logger.error(f"Error creating state representation: {e}")
            return "0_0_0_0_0_0"  # Default state
    
    def select_action(self, state: str, available_actions: List[str] = None) -> str:
        """Select action using epsilon-greedy policy"""
        try:
            if available_actions is None:
                available_actions = self.action_space
            
            # Epsilon-greedy action selection
            if np.random.random() < self.epsilon:
                # Explore: random action
                action = np.random.choice(available_actions)
            else:
                # Exploit: best known action
                action_values = {action: self.q_table[state][action] for action in available_actions}
                action = max(action_values, key=action_values.get)
            
            return action
            
        except Exception as e:
            self.logger.error(f"Error selecting action: {e}")
            return np.random.choice(available_actions) if available_actions else "pathway_type"
    
    def calculate_reward(self, feedback_data: Dict[str, Any]) -> float:
        """Calculate reward based on user feedback and system performance"""
        try:
            reward = 0.0
            
            # Feedback-based reward
            rating = feedback_data.get('rating', 0)
            if rating >= 4:
                reward += 1.0  # Positive feedback
            elif rating >= 3:
                reward += 0.5  # Neutral feedback
            elif rating >= 2:
                reward -= 0.5  # Negative feedback
            else:
                reward -= 1.0  # Very negative feedback
            
            # Response time reward (faster is better)
            response_time = feedback_data.get('response_time', 0)
            if response_time < 5.0:  # Less than 5 seconds
                reward += 0.3
            elif response_time > 30.0:  # More than 30 seconds
                reward -= 0.3
            
            # Recommendation quality indicators
            if feedback_data.get('recommendation_used', False):
                reward += 0.5
            
            if feedback_data.get('pathway_followed', False):
                reward += 1.0
            
            # Penalty for invalid recommendations
            if not feedback_data.get('is_valid', True):
                reward -= 0.8
            
            return reward
            
        except Exception as e:
            self.logger.error(f"Error calculating reward: {e}")
            return 0.0
    
    def update_q_table(self, state: str, action: str, reward: float, next_state: str):
        """Update Q-table using Q-learning algorithm"""
        try:
            # Current Q-value
            current_q = self.q_table[state][action]
            
            # Maximum Q-value for next state
            max_next_q = max(self.q_table[next_state].values()) if self.q_table[next_state] else 0
            
            # Q-learning update
            new_q = current_q + self.learning_rate * (reward + self.discount_factor * max_next_q - current_q)
            self.q_table[state][action] = new_q
            
            # Store experience for replay
            self.experience_replay.append({
                'state': state,
                'action': action,
                'reward': reward,
                'next_state': next_state,
                'timestamp': datetime.now()
            })
            
            # Update performance metrics
            self.performance_metrics['learning_episodes'] += 1
            self.reward_history.append(reward)
            
        except Exception as e:
            self.logger.error(f"Error updating Q-table: {e}")
    
    def learn_from_feedback(self, student_data: Dict[str, Any], 
                          recommendation: Dict[str, Any], 
                          feedback_data: Dict[str, Any]):
        """Learn from user feedback and update the model"""
        try:
            # Get state representation
            state = self.get_state_representation(student_data)
            
            # Determine action taken (simplified)
            action = self._infer_action_from_recommendation(recommendation)
            
            # Calculate reward
            reward = self.calculate_reward(feedback_data)
            
            # Get next state (simplified - could be improved)
            next_state = self._predict_next_state(student_data, recommendation)
            
            # Update Q-table
            self.update_q_table(state, action, reward, next_state)
            
            # Update performance metrics
            self.performance_metrics['total_recommendations'] += 1
            if reward > 0:
                self.performance_metrics['positive_feedback'] += 1
            elif reward < 0:
                self.performance_metrics['negative_feedback'] += 1
            
            # Decay epsilon
            self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
            
            # Save model periodically
            if self.performance_metrics['learning_episodes'] % 100 == 0:
                self.save_model()
            
            self.logger.info(f"Learned from feedback: reward={reward:.2f}, epsilon={self.epsilon:.3f}")
            
        except Exception as e:
            self.logger.error(f"Error learning from feedback: {e}")
    
    def optimize_recommendation(self, student_data: Dict[str, Any], 
                              base_recommendation: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize recommendation using learned knowledge"""
        try:
            state = self.get_state_representation(student_data)
            
            # Get best actions for this state
            state_actions = self.q_table[state]
            if not state_actions:
                return base_recommendation
            
            # Sort actions by Q-value
            sorted_actions = sorted(state_actions.items(), key=lambda x: x[1], reverse=True)
            
            # Apply optimizations based on learned preferences
            optimized_recommendation = base_recommendation.copy()
            
            for action, q_value in sorted_actions[:3]:  # Top 3 actions
                if q_value > 0.5:  # Only apply if confidence is high
                    optimized_recommendation = self._apply_action_optimization(
                        optimized_recommendation, action, q_value
                    )
            
            return optimized_recommendation
            
        except Exception as e:
            self.logger.error(f"Error optimizing recommendation: {e}")
            return base_recommendation
    
    def get_learning_insights(self) -> Dict[str, Any]:
        """Get insights about the learning process"""
        try:
            total_episodes = self.performance_metrics['learning_episodes']
            if total_episodes == 0:
                return {"message": "No learning data available yet"}
            
            # Calculate success rate
            positive = self.performance_metrics['positive_feedback']
            negative = self.performance_metrics['negative_feedback']
            total_feedback = positive + negative
            success_rate = (positive / total_feedback * 100) if total_feedback > 0 else 0
            
            # Calculate average reward
            avg_reward = np.mean(list(self.reward_history)) if self.reward_history else 0
            
            # Get top performing states
            top_states = sorted(
                [(state, max(actions.values()) if actions else 0) 
                 for state, actions in self.q_table.items()],
                key=lambda x: x[1], reverse=True
            )[:5]
            
            return {
                "total_learning_episodes": total_episodes,
                "success_rate": round(success_rate, 2),
                "average_reward": round(avg_reward, 3),
                "current_epsilon": round(self.epsilon, 3),
                "q_table_size": len(self.q_table),
                "top_performing_states": top_states,
                "performance_metrics": self.performance_metrics
            }
            
        except Exception as e:
            self.logger.error(f"Error getting learning insights: {e}")
            return {"error": str(e)}
    
    def save_model(self):
        """Save the learned model"""
        try:
            model_data = {
                'q_table': dict(self.q_table),
                'epsilon': self.epsilon,
                'performance_metrics': self.performance_metrics,
                'reward_history': list(self.reward_history),
                'timestamp': datetime.now().isoformat()
            }
            
            with open(self.model_path, 'wb') as f:
                pickle.dump(model_data, f)
            
            self.logger.info(f"Model saved to {self.model_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving model: {e}")
    
    def load_model(self):
        """Load the learned model"""
        try:
            if os.path.exists(self.model_path):
                with open(self.model_path, 'rb') as f:
                    model_data = pickle.load(f)
                
                self.q_table = defaultdict(lambda: defaultdict(float), model_data.get('q_table', {}))
                self.epsilon = model_data.get('epsilon', 0.1)
                self.performance_metrics = model_data.get('performance_metrics', self.performance_metrics)
                self.reward_history = deque(model_data.get('reward_history', []), maxlen=1000)
                
                self.logger.info(f"Model loaded from {self.model_path}")
            else:
                self.logger.info("No existing model found, starting fresh")
                
        except Exception as e:
            self.logger.error(f"Error loading model: {e}")
    
    # Helper methods
    def _categorize_interests(self, interests: List[str]) -> int:
        """Categorize interests into numerical code"""
        tech_interests = ['programming', 'software', 'web development', 'cybersecurity', 'data science', 'ai', 'machine learning']
        business_interests = ['management', 'marketing', 'finance', 'entrepreneurship']
        creative_interests = ['design', 'art', 'music', 'writing']
        
        if any(interest.lower() in tech_interests for interest in interests):
            return 0  # Technical
        elif any(interest.lower() in business_interests for interest in interests):
            return 1  # Business
        elif any(interest.lower() in creative_interests for interest in interests):
            return 2  # Creative
        else:
            return 3  # Other
    
    def _encode_location(self, location: str) -> int:
        """Encode location preference"""
        tier1_cities = ['mumbai', 'delhi', 'bangalore', 'chennai', 'hyderabad', 'pune', 'kolkata']
        tier2_cities = ['ahmedabad', 'jaipur', 'surat', 'lucknow', 'kanpur', 'nagpur', 'indore']
        
        location_lower = location.lower()
        if any(city in location_lower for city in tier1_cities):
            return 0  # Tier 1
        elif any(city in location_lower for city in tier2_cities):
            return 1  # Tier 2
        else:
            return 2  # Other
    
    def _encode_field(self, field: str) -> int:
        """Encode preferred field"""
        field_mapping = {
            'engineering': 0, 'science': 1, 'commerce': 2, 'arts': 3,
            'management': 4, 'design': 5, 'medicine': 6
        }
        return field_mapping.get(field.lower(), 7)  # Default to 'other'
    
    def _encode_learning_style(self, mode: str) -> int:
        """Encode learning style"""
        mode_mapping = {
            'online': 0, 'offline': 1, 'hybrid': 2
        }
        return mode_mapping.get(mode.lower(), 2)  # Default to hybrid
    
    def _infer_action_from_recommendation(self, recommendation: Dict[str, Any]) -> str:
        """Infer the action taken from the recommendation"""
        pathway = recommendation.get('recommended_pathway', '').lower()
        
        if 'b.tech' in pathway or 'engineering' in pathway:
            return 'pathway_type'
        elif 'online' in pathway or 'distance' in pathway:
            return 'learning_mode'
        elif 'certification' in pathway or 'diploma' in pathway:
            return 'course_duration'
        else:
            return 'pathway_type'  # Default
    
    def _predict_next_state(self, student_data: Dict[str, Any], recommendation: Dict[str, Any]) -> str:
        """Predict next state (simplified implementation)"""
        # This is a simplified implementation
        # In a real system, this would predict the student's next state based on the recommendation
        return self.get_state_representation(student_data)
    
    def _apply_action_optimization(self, recommendation: Dict[str, Any], action: str, confidence: float) -> Dict[str, Any]:
        """Apply optimization based on learned action"""
        optimized = recommendation.copy()
        
        if action == 'pathway_type' and confidence > 0.7:
            # Optimize pathway type based on learned preferences
            pathway = optimized.get('recommended_pathway', '')
            if 'b.sc' in pathway.lower() and confidence > 0.8:
                optimized['recommended_pathway'] = pathway.replace('B.Sc', 'B.Tech')
        
        elif action == 'learning_mode' and confidence > 0.7:
            # Optimize learning mode
            if 'online' not in pathway.lower() and confidence > 0.8:
                optimized['recommended_pathway'] += ' (Online/Hybrid options available)'
        
        return optimized
