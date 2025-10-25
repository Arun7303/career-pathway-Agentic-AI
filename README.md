# Agentic AI Course Pathway Recommender

A professional and advanced web application that uses agentic AI to provide personalized educational pathway recommendations for students. The system employs multiple specialized AI agents working together to analyze student profiles and generate comprehensive, validated recommendations.

## 🚀 Features

### 🤖 Agentic AI Architecture
- **Data Analysis Agent**: Analyzes academic performance, interests, and learning styles
- **Recommendation Agent**: Generates personalized pathways using Google Gemini AI
- **Validation Agent**: Validates recommendations for quality and feasibility

### 🎯 Core Functionality
- **Personalized Recommendations**: AI-powered pathway suggestions based on student profiles
- **Academic Analysis**: Comprehensive analysis of academic performance and potential
- **Interest Mapping**: Categorization and analysis of student interests
- **Budget Feasibility**: Cost analysis and funding recommendations
- **Validation System**: Multi-level validation for recommendation quality

### 💾 Database & Storage
- **SQLite Database**: Secure storage of student data and recommendations
- **Student Management**: Complete student profile management with contact information
- **Feedback System**: Rating and feedback collection for continuous improvement
- **Analytics Tracking**: Comprehensive analytics and usage statistics

### 🎨 Professional UI/UX
- **Modern Design**: Clean, professional interface with Bootstrap 5
- **Responsive Layout**: Mobile-first design that works on all devices
- **Interactive Elements**: Real-time form validation and user feedback
- **Loading Animations**: Professional loading states and progress indicators

### 📊 Analytics Dashboard
- **System Health Monitoring**: Real-time health checks for all AI agents
- **Performance Metrics**: Detailed analytics on system performance
- **Student Statistics**: Comprehensive student data visualization
- **Usage Analytics**: Track system usage and recommendation patterns

## 🛠️ Technology Stack

### Backend
- **Flask 2.3.3**: Web framework
- **Python 3.9+**: Programming language
- **SQLite**: Database
- **Google Generative AI**: AI model integration
- **Scikit-learn**: Machine learning algorithms

### Frontend
- **Bootstrap 5**: CSS framework
- **JavaScript**: Interactive functionality
- **Chart.js**: Data visualization
- **Font Awesome**: Icons

### AI & ML
- **Google Gemini Pro**: Advanced AI model
- **TF-IDF Vectorization**: Text similarity analysis
- **Cosine Similarity**: Student profile matching
- **Custom ML Algorithms**: Specialized recommendation algorithms

## 📁 Project Structure

```
code/
├── agents/                     # AI Agents
│   ├── __init__.py
│   ├── base_agent.py          # Base agent class
│   ├── data_analysis_agent.py # Data analysis agent
│   ├── recommendation_agent.py # Recommendation agent
│   ├── validation_agent.py    # Validation agent
│   └── agentic_orchestrator.py # Main orchestrator
├── models/                     # ML Models
│   ├── __init__.py
│   ├── data_processor.py      # Data processing
│   └── recommendation_model.py # Legacy recommendation model
├── templates/                  # HTML Templates
│   ├── base.html
│   ├── index.html
│   ├── student_form.html
│   ├── recommendation.html
│   ├── dashboard.html
│   ├── students_list.html
│   ├── student_detail.html
│   ├── insights.html
│   └── error.html
├── static/                     # Static Files
│   ├── css/
│   ├── js/
│   └── images/
├── data/                       # Data Files
│   └── student_data.csv
├── utils/                      # Utilities
│   └── __init__.py
├── app.py                      # Main Flask application
├── config.py                   # Configuration
├── database.py                 # Database management
├── requirements.txt            # Dependencies
└── README.md                   # This file
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.9 or higher
- pip (Python package installer)
- Git

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd "agentic ai /code"
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   SECRET_KEY=your-secret-key-here
   GOOGLE_API_KEY=your-google-api-key-here
   ```

5. **Initialize the database**
   The database will be automatically created when you first run the application.

6. **Run the application**
   ```bash
   python app.py
   ```

7. **Access the application**
   Open your browser and navigate to `http://localhost:5000`

## 🔧 Configuration

### Google API Setup
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add the key to your `.env` file as `GOOGLE_API_KEY`

### Database Configuration
The application uses SQLite by default. The database file (`student_pathway.db`) will be created automatically in the project root.

## 📖 Usage Guide

### For Students
1. **Navigate to the application** and click "Get AI Recommendation"
2. **Fill out the form** with your personal and academic information
3. **Submit the form** and wait for AI processing
4. **Review your personalized recommendation** with detailed pathway information
5. **Rate the recommendation** to help improve the system

### For Administrators
1. **Access the dashboard** at `/dashboard` for system analytics
2. **View student list** at `/students` to manage student data
3. **Monitor system health** through the analytics dashboard
4. **Export data** and view comprehensive reports

## 🔍 API Endpoints

### Main Routes
- `GET /` - Home page
- `GET /recommendation-form` - Student form
- `POST /get-recommendation` - Process recommendation request
- `GET /dashboard` - Analytics dashboard
- `GET /students` - Student list
- `GET /student/<id>` - Student details

### API Endpoints
- `GET /api/health` - System health check
- `GET /api/analytics` - System analytics
- `POST /api/recommend` - Programmatic recommendation
- `POST /feedback` - Submit feedback

## 🤖 AI Agents Details

### Data Analysis Agent
- **Purpose**: Analyzes student academic performance and interests
- **Capabilities**:
  - Academic performance categorization
  - Interest analysis and categorization
  - Learning style assessment
  - Psychological profiling
  - Constraint identification

### Recommendation Agent
- **Purpose**: Generates personalized educational pathways
- **Capabilities**:
  - AI-powered pathway generation using Google Gemini
  - Career opportunity mapping
  - Course and skill recommendations
  - Timeline and milestone creation
  - Alternative pathway suggestions

### Validation Agent
- **Purpose**: Validates and ensures recommendation quality
- **Capabilities**:
  - Academic fit validation
  - Budget feasibility assessment
  - Interest alignment verification
  - General feasibility checks
  - Quality assurance scoring

## 📊 Database Schema

### Students Table
- `id` - Primary key
- `name` - Student name
- `mobile_number` - Contact number
- `email` - Email address
- `education_type` - HSC/Diploma
- `ssc_percent`, `hsc_percent`, `diploma_percent` - Academic scores
- `subjects` - Subject stream
- `interests` - JSON array of interests
- `preferred_field` - Preferred field of study
- `preferred_mode` - Learning mode preference
- `budget` - Annual budget
- `location_preference` - Preferred location
- `created_at`, `updated_at` - Timestamps

### Recommendations Table
- `id` - Primary key
- `student_id` - Foreign key to students
- `recommended_pathway` - AI-generated pathway
- `reasoning` - Explanation for recommendation
- `career_opportunities` - JSON array of opportunities
- `suggested_courses` - JSON array of courses
- `skills_to_develop` - JSON array of skills
- `additional_recommendations` - Additional advice
- `confidence_score` - AI confidence score
- `created_at` - Timestamp

### Feedback Table
- `id` - Primary key
- `student_id` - Foreign key to students
- `recommendation_id` - Foreign key to recommendations
- `rating` - 1-5 star rating
- `feedback_text` - Text feedback
- `created_at` - Timestamp

## 🔒 Security Features

- **Input Validation**: Comprehensive form validation
- **SQL Injection Protection**: Parameterized queries
- **XSS Protection**: Template escaping
- **CSRF Protection**: Flask-WTF integration
- **Data Sanitization**: Input sanitization and validation

## 🚀 Deployment

### Local Development
```bash
python app.py
```

### Production Deployment
1. Set `FLASK_ENV=production`
2. Use a production WSGI server like Gunicorn
3. Set up a reverse proxy with Nginx
4. Configure SSL certificates
5. Set up monitoring and logging

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

## 📈 Performance Optimization

- **Caching**: Implement Redis for session and data caching
- **Database Indexing**: Optimize database queries
- **API Rate Limiting**: Implement rate limiting for API endpoints
- **CDN**: Use CDN for static assets
- **Load Balancing**: Implement load balancing for high traffic

## 🧪 Testing

### Unit Tests
```bash
python -m pytest tests/
```

### Integration Tests
```bash
python -m pytest tests/integration/
```

### Load Testing
```bash
# Using Apache Bench
ab -n 1000 -c 10 http://localhost:5000/
```

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

## 🔮 Future Enhancements

- **Multi-language Support**: Internationalization
- **Advanced Analytics**: Machine learning insights
- **Mobile App**: Native mobile application
- **Integration APIs**: Third-party integrations
- **Advanced AI Models**: Integration with more AI models
- **Real-time Chat**: AI-powered chat support
- **Video Recommendations**: Video-based pathway explanations

## 📊 System Requirements

### Minimum Requirements
- Python 3.9+
- 2GB RAM
- 1GB storage
- Internet connection for AI API calls

### Recommended Requirements
- Python 3.11+
- 4GB RAM
- 5GB storage
- High-speed internet connection

---

**Built with ❤️ using Flask, Google AI, and modern web technologies**
