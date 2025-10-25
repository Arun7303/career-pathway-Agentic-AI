import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
import re

class DataProcessor:
    def __init__(self, data_path):
        self.data_path = data_path
        self.df = None
        self.label_encoders = {}
        self.scaler = StandardScaler()
        self.tfidf_vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
        self.load_data()
        
    def load_data(self):
        """Load and preprocess the dataset"""
        try:
            self.df = pd.read_csv(self.data_path)
            self.preprocess_data()
            print(f"Data loaded successfully with {len(self.df)} records")
        except Exception as e:
            print(f"Error loading data: {e}")
            # Create empty dataframe with expected columns if file not found
            self.df = pd.DataFrame(columns=[
                'student_id', 'education_type', 'ssc_percent', 'hsc_percent', 
                'diploma_percent', 'subjects', 'interests', 'preferred_field',
                'preferred_mode', 'budget', 'location_preference', 'target_pathway', 'pathway_label'
            ])
        
    def preprocess_data(self):
        """Preprocess the dataset"""
        if self.df.empty:
            print("No data available for preprocessing")
            return
            
        # Handle missing values - convert to string first to avoid dtype warnings
        for col in self.df.columns:
            if self.df[col].dtype == 'object':
                self.df[col] = self.df[col].astype(str).replace('nan', '')
            else:
                self.df[col] = self.df[col].fillna(0)
        
        # Convert percentage columns to numeric
        percentage_columns = ['ssc_percent', 'hsc_percent', 'diploma_percent']
        for col in percentage_columns:
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce').fillna(0)
        
        # Encode categorical variables
        categorical_columns = ['education_type', 'subjects', 'preferred_field', 
                             'preferred_mode', 'location_preference']
        
        for col in categorical_columns:
            if col in self.df.columns and len(self.df[col]) > 0:
                try:
                    self.label_encoders[col] = LabelEncoder()
                    self.df[f'{col}_encoded'] = self.label_encoders[col].fit_transform(self.df[col].astype(str))
                except Exception as e:
                    print(f"Error encoding {col}: {e}")
                    self.df[f'{col}_encoded'] = 0
        
        # Process interests (convert list strings to actual lists)
        self.df['interests_processed'] = self.df['interests'].apply(self.process_interests)
        
        # Create combined features for similarity
        self.df['combined_features'] = self.df.apply(self.combine_features, axis=1)
        
        # Fit TF-IDF on combined features
        if len(self.df) > 0:
            self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(self.df['combined_features'])
        else:
            self.tfidf_matrix = None

    def get_available_options(self):
        """Get all available options for form dropdowns"""
        if self.df.empty:
            return self._get_default_options()
            
        options = {
            'education_types': sorted(self.df['education_type'].dropna().unique().tolist()),
            'subjects': sorted(self.df['subjects'].dropna().unique().tolist()),
            'preferred_fields': sorted(self.df['preferred_field'].dropna().unique().tolist()),
            'preferred_modes': sorted(self.df['preferred_mode'].dropna().unique().tolist()),
            'locations': sorted(self.df['location_preference'].dropna().unique().tolist()),
            'interests': self._get_all_interests()
        }
        return options

    def _get_default_options(self):
        """Return default options when no data is available"""
        return {
            'education_types': ['HSC', 'Diploma'],
            'subjects': ['PCM', 'PCB', 'Commerce', 'Arts', 'CS'],
            'preferred_fields': ['Engineering', 'Science', 'Commerce', 'Arts', 'Design', 'Management'],
            'preferred_modes': ['Online', 'Offline', 'Hybrid'],
            'locations': ['Mumbai', 'Delhi', 'Bangalore', 'Kolkata', 'Chennai', 'Pune', 'Nashik'],
            'interests': [
                'Research', 'Cybersecurity', 'Finance', 'Robotics', 'Psychology',
                'Web Development', 'Data Science', 'UX', 'Marketing', 'Management',
                'AI', 'Design'
            ]
        }

    def _get_all_interests(self):
        """Extract all unique interests from the dataset"""
        all_interests = set()
        for interests_list in self.df['interests_processed']:
            all_interests.update(interests_list)
        return sorted(list(all_interests))
        
    def process_interests(self, interests_str):
        """Convert interests string to list"""
        if isinstance(interests_str, str):
            # Remove brackets and quotes, then split
            interests_str = re.sub(r'[\[\]\'\"]', '', interests_str)
            return [interest.strip() for interest in interests_str.split(',') if interest.strip()]
        elif isinstance(interests_str, list):
            return interests_str
        return []
    
    def combine_features(self, row):
        """Combine all features into a single string for similarity comparison"""
        features = []
        
        # Academic scores
        features.extend([
            f"ssc_{row.get('ssc_percent', 0)}",
            f"hsc_{row.get('hsc_percent', 0)}",
            f"diploma_{row.get('diploma_percent', 0)}"
        ])
        
        # Categorical features
        features.extend([
            f"edu_type_{row.get('education_type', '')}",
            f"subjects_{row.get('subjects', '')}",
            f"field_{row.get('preferred_field', '')}",
            f"mode_{row.get('preferred_mode', '')}",
            f"location_{row.get('location_preference', '')}"
        ])
        
        # Interests
        interests = self.process_interests(row.get('interests', ''))
        features.extend([f"interest_{interest}" for interest in interests])
        
        # Budget
        features.append(f"budget_{row.get('budget', 0)}")
        
        return ' '.join(features)
    
    def get_similar_students(self, student_features, top_n=5):
        """Find similar students based on features"""
        if self.tfidf_matrix is None or len(self.df) == 0:
            return []
            
        try:
            # Transform input features
            input_vector = self.tfidf_vectorizer.transform([student_features])
            
            # Calculate similarity
            similarities = cosine_similarity(input_vector, self.tfidf_matrix)
            
            # Get top similar students
            similar_indices = similarities.argsort()[0][-top_n:][::-1]
            
            similar_students = []
            for idx in similar_indices:
                if similarities[0][idx] > 0:  # Only include if similarity > 0
                    student_data = self.df.iloc[idx].to_dict()
                    student_data['similarity_score'] = float(similarities[0][idx])
                    similar_students.append(student_data)
            
            return similar_students
        except Exception as e:
            print(f"Error finding similar students: {e}")
            return []
    
    def get_pathway_stats(self, pathway_label):
        """Get statistics for a particular pathway"""
        if self.df.empty:
            return None
            
        pathway_data = self.df[self.df['pathway_label'] == pathway_label]
        
        if pathway_data.empty:
            return None
            
        return {
            'average_ssc': pathway_data['ssc_percent'].mean(),
            'average_hsc': pathway_data['hsc_percent'].mean(),
            'average_diploma': pathway_data['diploma_percent'].mean(),
            'common_interests': self.get_common_interests(pathway_data),
            'popular_locations': pathway_data['location_preference'].value_counts().head(3).to_dict(),
            'count': len(pathway_data)
        }
    
    def get_common_interests(self, data):
        """Extract common interests from pathway data"""
        all_interests = []
        for interests in data['interests_processed']:
            all_interests.extend(interests)
        
        from collections import Counter
        return dict(Counter(all_interests).most_common(5))