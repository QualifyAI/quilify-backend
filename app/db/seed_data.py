"""
Script to seed initial data for the application
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

# Niches collection
niches = [
    {
        "id": 1,
        "name": "Web Development",
        "icon": "code",
        "description": "Full-stack web development with modern frameworks and technologies"
    },
    {
        "id": 2,
        "name": "Data Science",
        "icon": "database",
        "description": "Data analysis, machine learning, and statistical modeling"
    },
    {
        "id": 3,
        "name": "Mobile Development",
        "icon": "smartphone",
        "description": "Native and cross-platform mobile app development"
    },
    {
        "id": 4,
        "name": "DevOps",
        "icon": "cloud",
        "description": "Continuous integration, deployment, and cloud infrastructure"
    },
    {
        "id": 5,
        "name": "UI/UX Design",
        "icon": "design",
        "description": "User interface and experience design for digital products"
    },
    {
        "id": 6,
        "name": "Cybersecurity",
        "icon": "shield",
        "description": "Network security, penetration testing, and secure coding practices"
    },
    {
        "id": 7,
        "name": "Artificial Intelligence",
        "icon": "brain",
        "description": "Machine learning, deep learning, and AI applications"
    }
]

# Path questions collection
questions = [
    # Web Development Questions
    {
        "id": "web_exp",
        "label": "What is your current level of experience with web development?",
        "options": [
            "Beginner - No prior experience", 
            "Novice - Basic HTML/CSS knowledge", 
            "Intermediate - Some experience with JavaScript", 
            "Advanced - Professional experience"
        ],
        "nicheId": 1
    },
    {
        "id": "web_goal",
        "label": "What is your primary goal in web development?",
        "options": [
            "Frontend development", 
            "Backend development", 
            "Full-stack development", 
            "Specialized (e.g., WebGL, WebRTC)"
        ],
        "nicheId": 1
    },
    {
        "id": "web_time",
        "label": "How much time can you dedicate to learning weekly?",
        "options": [
            "1-5 hours", 
            "6-10 hours", 
            "11-20 hours", 
            "20+ hours"
        ],
        "nicheId": 1
    },
    {
        "id": "web_interest",
        "label": "Which technologies are you most interested in?",
        "options": [
            "React/Next.js ecosystem", 
            "Vue/Nuxt.js ecosystem", 
            "Angular ecosystem", 
            "Node.js/Express", 
            "Python/Django/Flask"
        ],
        "nicheId": 1
    },
    
    # Data Science Questions
    {
        "id": "ds_exp",
        "label": "What is your current level of experience with data science?",
        "options": [
            "Beginner - No prior experience", 
            "Novice - Basic statistics knowledge", 
            "Intermediate - Some experience with data analysis", 
            "Advanced - Professional experience"
        ],
        "nicheId": 2
    },
    {
        "id": "ds_goal",
        "label": "What is your primary goal in data science?",
        "options": [
            "Data analysis and visualization", 
            "Machine learning and predictive modeling", 
            "Deep learning and neural networks", 
            "Big data processing", 
            "Natural language processing"
        ],
        "nicheId": 2
    },
    {
        "id": "ds_time",
        "label": "How much time can you dedicate to learning weekly?",
        "options": [
            "1-5 hours", 
            "6-10 hours", 
            "11-20 hours", 
            "20+ hours"
        ],
        "nicheId": 2
    },
    {
        "id": "ds_math",
        "label": "What is your background in mathematics?",
        "options": [
            "Basic - High school level", 
            "Intermediate - Undergraduate level", 
            "Advanced - Graduate level", 
            "Expert - Research level"
        ],
        "nicheId": 2
    },
    
    # Mobile Development Questions
    {
        "id": "mobile_exp",
        "label": "What is your current level of experience with mobile development?",
        "options": [
            "Beginner - No prior experience", 
            "Novice - Basic app development knowledge", 
            "Intermediate - Some experience building apps", 
            "Advanced - Professional experience"
        ],
        "nicheId": 3
    },
    {
        "id": "mobile_goal",
        "label": "What is your primary goal in mobile development?",
        "options": [
            "iOS development", 
            "Android development", 
            "Cross-platform development", 
            "Mobile game development"
        ],
        "nicheId": 3
    },
    {
        "id": "mobile_time",
        "label": "How much time can you dedicate to learning weekly?",
        "options": [
            "1-5 hours", 
            "6-10 hours", 
            "11-20 hours", 
            "20+ hours"
        ],
        "nicheId": 3
    },
    {
        "id": "mobile_tech",
        "label": "Which technologies are you most interested in?",
        "options": [
            "Swift/SwiftUI", 
            "Kotlin/Jetpack Compose", 
            "React Native", 
            "Flutter", 
            "Unity/C#"
        ],
        "nicheId": 3
    }
]

async def seed_data():
    """
    Seed the database with initial data
    """
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_NAME]
    
    # Seed niches
    await db.niches.delete_many({})  # Clear existing data
    if await db.niches.count_documents({}) == 0:
        await db.niches.insert_many(niches)
        print(f"Inserted {len(niches)} niches")
    
    # Seed questions
    await db.path_questions.delete_many({})  # Clear existing data
    if await db.path_questions.count_documents({}) == 0:
        await db.path_questions.insert_many(questions)
        print(f"Inserted {len(questions)} path questions")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_data()) 