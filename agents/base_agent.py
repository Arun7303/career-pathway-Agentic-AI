from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import google.generativeai as genai
from config import Config
import json
import logging

class BaseAgent(ABC):
    """Base class for all AI agents in the system"""
    
    def __init__(self, agent_name: str, model_name: str = None):
        self.agent_name = agent_name
        self.model_name = model_name or Config.MODEL_NAME
        self.model = None
        self.is_available = False
        self.logger = logging.getLogger(f"Agent.{agent_name}")
        
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the AI model"""
        try:
            if Config.GOOGLE_API_KEY and Config.GOOGLE_API_KEY != 'your_actual_google_api_key_here':
                genai.configure(api_key=Config.GOOGLE_API_KEY)
                self.model = genai.GenerativeModel(self.model_name)
                self.is_available = True
                self.logger.info(f"{self.agent_name} initialized successfully")
            else:
                self.logger.warning(f"{self.agent_name} - Google API key not found")
                self.is_available = False
        except Exception as e:
            self.logger.error(f"Failed to initialize {self.agent_name}: {e}")
            self.is_available = False
    
    @abstractmethod
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process data and return results"""
        pass
    
    def generate_response(self, prompt: str, max_retries: int = 3) -> Optional[str]:
        """Generate response using the AI model with retry logic"""
        if not self.is_available:
            self.logger.warning(f"{self.agent_name} - Model not available")
            return None
        
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(prompt)
                if response and response.text:
                    return response.text
                else:
                    self.logger.warning(f"{self.agent_name} - Empty response on attempt {attempt + 1}")
            except Exception as e:
                self.logger.error(f"{self.agent_name} - Error on attempt {attempt + 1}: {e}")
                if attempt == max_retries - 1:
                    return None
        
        return None
    
    def parse_json_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """Parse JSON response from AI model"""
        try:
            # Clean the response text
            cleaned_text = response_text.strip()
            
            # Try to find JSON in the response
            import re
            json_match = re.search(r'\{.*\}', cleaned_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                return json.loads(json_str)
            else:
                self.logger.warning(f"{self.agent_name} - No JSON found in response")
                return None
        except json.JSONDecodeError as e:
            self.logger.error(f"{self.agent_name} - JSON parsing error: {e}")
            return None
        except Exception as e:
            self.logger.error(f"{self.agent_name} - Error parsing response: {e}")
            return None
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status information"""
        return {
            'agent_name': self.agent_name,
            'model_name': self.model_name,
            'is_available': self.is_available,
            'status': 'active' if self.is_available else 'inactive'
        }
