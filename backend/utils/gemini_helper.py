import google.generativeai as genai
import os
from dotenv import load_dotenv
import re

load_dotenv()

class GeminiHelper:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        genai.configure(api_key=api_key)
        
        # Try different model names
        model_names = [
            "gemini-1.5-pro",
            "gemini-1.5-flash",
            "models/gemini-1.5-pro",
            "models/gemini-1.5-flash",
        ]
        
        self.model = None
        for model_name in model_names:
            try:
                test_model = genai.GenerativeModel(model_name)
                test_response = test_model.generate_content("Hello")
                if test_response:
                    self.model = test_model
                    print(f"✅ Using model: {model_name}")
                    break
            except Exception as e:
                continue
        
        if self.model is None:
            print("❌ No working model found! Using fallback mode.")
    
    def generate_response(self, prompt):
        if self.model is None:
            return self._generate_fallback_response(prompt)
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"⚠️ Error: {str(e)}")
            return self._generate_fallback_response(prompt)
    
    def _generate_fallback_response(self, prompt):
        """Generate clean fallback response"""
        if "interview questions" in prompt.lower():
            # Extract job role
            job_role = "professional"
            for line in prompt.split('\n'):
                if "Job:" in line or "Job Role:" in line:
                    job_role = line.split(":")[-1].strip()
                    break
            
            # Get job-specific questions
            questions = self._get_clean_job_questions(job_role)
            return "\n".join([f"{i+1}. {q}" for i, q in enumerate(questions)])
        
        elif "evaluate" in prompt.lower():
            return """
SCORE: 75
FEEDBACK: Good attempt with clear communication. Could add more specific examples.
STRENGTHS: Clear structure, relevant points, good communication.
IMPROVEMENTS: Add technical depth, include specific examples, provide more detail.
SUGGESTED_ANSWER: Here is a more comprehensive answer with specific examples and technical depth...
SKILLS_TO_IMPROVE: Technical knowledge, practical application, depth of understanding.
LEARNING_TOPICS: Advanced concepts, industry best practices, current trends.
"""
        
        elif "report" in prompt.lower():
            return """
1. EXECUTIVE SUMMARY
   Overall performance is good with some areas for improvement.

2. SCORE BREAKDOWN
   - Technical knowledge: 75%
   - Communication: 80%
   - Problem-solving: 70%

3. STRENGTHS ANALYSIS
   - Good communication skills
   - Clear thinking process
   - Relevant experience

4. AREAS FOR IMPROVEMENT
   - Technical depth
   - Specific examples
   - Practical experience

5. RECOMMENDED LEARNING PATH
   - Focus on practical projects
   - Study advanced concepts
   - Practice with real-world scenarios

6. FINAL VERDICT
   - Good potential, needs more preparation
   - Recommended to practice more technical questions
"""
        
        return "Response generated from fallback system."
    
    def _get_clean_job_questions(self, job_role):
        """Get clean, formatted questions based on job role"""
        role_lower = job_role.lower()
        
        # Software/Developer questions
        if any(word in role_lower for word in ['software', 'developer', 'engineer', 'programmer', 'python', 'java', 'javascript']):
            return [
                "Explain the difference between object-oriented programming and functional programming with examples.",
                "What are the key principles of clean code and how do you apply them in your daily work?",
                "Describe your experience with version control systems like Git and your typical workflow.",
                "How do you handle debugging and troubleshooting in your development process?",
                "Explain the concept of microservices and their advantages over monolithic architecture.",
                "What is your approach to code reviews and maintaining code quality in a team?",
                "How do you stay updated with the latest technologies and industry trends?",
                "Describe a challenging technical problem you solved and your approach to finding the solution."
            ]
        # Data Science/Analyst questions
        elif any(word in role_lower for word in ['data', 'analyst', 'science', 'machine', 'learning', 'ai']):
            return [
                "Explain the difference between supervised and unsupervised learning with real-world examples.",
                "What data preprocessing techniques do you commonly use and why are they important?",
                "How do you handle missing data in a dataset and what methods do you prefer?",
                "Explain the concept of overfitting and how do you prevent it in your models?",
                "What is your experience with SQL and database management in data projects?",
                "How do you visualize data to communicate insights effectively to stakeholders?",
                "Describe a data project you worked on from start to finish and your role in it.",
                "What statistical methods are you most comfortable with and when do you use them?"
            ]
        # UI/UX Designer questions
        elif any(word in role_lower for word in ['ui', 'ux', 'designer', 'design', 'creative']):
            return [
                "Explain the difference between UI and UX design and why both are important.",
                "What is your design process from research to final delivery and handoff?",
                "How do you incorporate user feedback into your design iterations?",
                "Describe a project where you successfully improved the user experience.",
                "What design tools are you proficient in and which one is your favorite?",
                "How do you ensure your designs are accessible to users with disabilities?",
                "Explain the importance of prototyping and user testing in design.",
                "How do you stay updated with the latest design trends and best practices?"
            ]
        # Default questions for any role
        else:
            return [
                f"Describe your experience and skills relevant to {job_role}.",
                "What makes you a good fit for this role and how can you add value?",
                "How do you handle challenges and difficult situations at work?",
                "Describe a project you're proud of and your contribution to its success.",
                "Where do you see yourself in 5 years and how does this role fit in?",
                "What are your key strengths and how do they relate to this position?",
                "How do you manage your time and prioritize multiple tasks effectively?",
                "Tell me about a time you worked in a team and faced a conflict. How did you handle it?"
            ]
    
    def evaluate_answer(self, question, answer, context):
        prompt = f"""
        You are an expert interviewer. Evaluate this answer:
        
        Job Role: {context.get('job_role', '')}
        Experience: {context.get('experience_level', '')}
        Question: {question}
        Answer: {answer}
        
        Provide EXACT format:
        SCORE: [0-100]
        FEEDBACK: [Detailed feedback]
        STRENGTHS: [List strengths]
        IMPROVEMENTS: [Areas for improvement]
        SUGGESTED_ANSWER: [Better answer]
        SKILLS_TO_IMPROVE: [Skills needed]
        LEARNING_TOPICS: [Topics to study]
        """
        
        return self.generate_response(prompt)
    
    def generate_interview_questions(self, context):
        num_questions = context.get('number_of_questions', 5)
        job_role = context.get('job_role', '')
        experience = context.get('experience_level', '')
        skills = ', '.join(context.get('skills', []))
        interview_type = context.get('interview_type', '')
        difficulty = context.get('difficulty_level', '')
        
        # Get clean questions based on job role
        all_questions = self._get_clean_job_questions(job_role)
        
        # Select exactly the number of questions requested
        if len(all_questions) >= num_questions:
            selected = all_questions[:num_questions]
        else:
            # If not enough questions, repeat with variations
            selected = all_questions
            while len(selected) < num_questions:
                # Add generic questions
                generic = [
                    f"Tell me about your experience with {job_role}.",
                    "What are your career goals and how does this role align with them?",
                    "Describe a time you showed leadership in a project.",
                    "How do you handle feedback and criticism?",
                    "What motivates you to perform well at work?"
                ]
                for q in generic:
                    if q not in selected:
                        selected.append(q)
                    if len(selected) >= num_questions:
                        break
        
        return selected[:num_questions]
    
    def generate_final_report(self, interview_data):
        prompt = f"""
        Generate a detailed interview report for:
        
        Name: {interview_data.get('full_name', '')}
        Job: {interview_data.get('job_role', '')}
        Experience: {interview_data.get('experience_level', '')}
        Skills: {', '.join(interview_data.get('skills', []))}
        Total Questions: {interview_data.get('number_of_questions', 0)}
        
        Provide a comprehensive report with:
        1. EXECUTIVE SUMMARY
        2. SCORE BREAKDOWN
        3. STRENGTHS ANALYSIS
        4. AREAS FOR IMPROVEMENT
        5. RECOMMENDED LEARNING PATH
        6. FINAL VERDICT
        """
        
        return self.generate_response(prompt)