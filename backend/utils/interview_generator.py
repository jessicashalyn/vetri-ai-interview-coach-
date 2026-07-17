from .gemini_helper import GeminiHelper
from models.interview import InterviewData
import re
import logging

logger = logging.getLogger(__name__)

class InterviewGenerator:
    def __init__(self):
        self.gemini = GeminiHelper()
        self.interview_data = InterviewData()
        self.current_question_index = 0
        self._questions_generated = False
    
    def start_interview(self, user_input):
        """Start interview and generate questions based on user input"""
        # Store user input
        self.interview_data.full_name = user_input.get('full_name', '')
        self.interview_data.job_role = user_input.get('job_role', '')
        self.interview_data.experience_level = user_input.get('experience_level', '')
        self.interview_data.skills = user_input.get('skills', [])
        self.interview_data.interview_type = user_input.get('interview_type', '')
        self.interview_data.difficulty_level = user_input.get('difficulty_level', '')
        self.interview_data.number_of_questions = int(user_input.get('number_of_questions', 5))
        
        # Build context
        context = {
            'job_role': self.interview_data.job_role,
            'experience_level': self.interview_data.experience_level,
            'skills': self.interview_data.skills,
            'interview_type': self.interview_data.interview_type,
            'difficulty_level': self.interview_data.difficulty_level,
            'number_of_questions': self.interview_data.number_of_questions
        }
        
        # Generate questions
        questions = self.gemini.generate_interview_questions(context)
        
        # Ensure we have the right number of clean questions
        if not questions or len(questions) == 0:
            questions = self.gemini._get_clean_job_questions(
                self.interview_data.job_role
            )[:self.interview_data.number_of_questions]
        
        # Clean any formatting issues
        clean_questions = []
        for q in questions:
            q = q.strip()
            # Remove any "Question X:" prefix
            q = re.sub(r'^Question\s*\d+[:.]\s*', '', q, flags=re.IGNORECASE)
            q = re.sub(r'^\d+[:.]\s*', '', q)
            if q and len(q) > 5:
                clean_questions.append(q)
        
        # If we lost questions during cleaning, get more
        if len(clean_questions) < self.interview_data.number_of_questions:
            extra = self.gemini._get_clean_job_questions(
                self.interview_data.job_role
            )
            for q in extra:
                if q not in clean_questions:
                    clean_questions.append(q)
                if len(clean_questions) >= self.interview_data.number_of_questions:
                    break
        
        # Store exactly the number requested
        self.interview_data.questions = clean_questions[:self.interview_data.number_of_questions]
        self.current_question_index = 0
        self._questions_generated = True
        
        # Log generated questions
        logger.info(f"✅ Generated {len(self.interview_data.questions)} questions for {self.interview_data.job_role}")
        for i, q in enumerate(self.interview_data.questions, 1):
            logger.info(f"  Q{i}: {q}")
        
        return self.interview_data.questions
    
    def get_next_question(self):
        """Get the next question automatically"""
        if not self._questions_generated:
            logger.warning("❌ Questions not generated yet")
            return None
        
        if self.current_question_index < len(self.interview_data.questions):
            question = self.interview_data.questions[self.current_question_index]
            self.current_question_index += 1
            return {
                'question': question,
                'index': self.current_question_index,
                'total': len(self.interview_data.questions)
            }
        
        logger.info("✅ All questions completed")
        return None
    
    def evaluate_answer(self, question, answer):
        context = {
            'job_role': self.interview_data.job_role,
            'experience_level': self.interview_data.experience_level,
            'interview_type': self.interview_data.interview_type,
            'difficulty_level': self.interview_data.difficulty_level
        }
        
        evaluation_text = self.gemini.evaluate_answer(question, answer, context)
        evaluation = self._parse_evaluation(evaluation_text)
        evaluation['question'] = question
        evaluation['answer'] = answer
        
        # Ensure score is valid
        if evaluation['score'] < 0:
            evaluation['score'] = 0
        elif evaluation['score'] > 100:
            evaluation['score'] = 100
        
        self.interview_data.evaluations.append(evaluation)
        logger.info(f"📊 Score for question: {evaluation['score']}")
        return evaluation
    
    def _parse_evaluation(self, text):
        evaluation = {
            'score': 0,
            'feedback': '',
            'strengths': '',
            'improvements': '',
            'suggested_answer': '',
            'skills_to_improve': '',
            'learning_topics': ''
        }
        
        # Extract score
        score_match = re.search(r'SCORE:\s*(\d+)', text, re.IGNORECASE)
        if score_match:
            try:
                evaluation['score'] = int(score_match.group(1))
            except:
                evaluation['score'] = 70
        
        # Extract other fields
        patterns = {
            'feedback': r'FEEDBACK:\s*(.*?)(?=STRENGTHS:|IMPROVEMENTS:|SUGGESTED_ANSWER:|$)',
            'strengths': r'STRENGTHS:\s*(.*?)(?=IMPROVEMENTS:|SUGGESTED_ANSWER:|$)',
            'improvements': r'IMPROVEMENTS:\s*(.*?)(?=SUGGESTED_ANSWER:|$)',
            'suggested_answer': r'SUGGESTED_ANSWER:\s*(.*?)(?=SKILLS_TO_IMPROVE:|LEARNING_TOPICS:|$)',
            'skills_to_improve': r'SKILLS_TO_IMPROVE:\s*(.*?)(?=LEARNING_TOPICS:|$)',
            'learning_topics': r'LEARNING_TOPICS:\s*(.*?)(?=$)'
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                evaluation[key] = match.group(1).strip()
        
        return evaluation
    
    def get_final_report(self):
        return self.gemini.generate_final_report(self.interview_data.to_dict())
    
    def get_overall_score(self):
        if not self.interview_data.evaluations:
            return 0
        total = sum(eval_data.get('score', 0) for eval_data in self.interview_data.evaluations)
        return round(total / len(self.interview_data.evaluations), 1)
    
    def get_interview_data(self):
        return self.interview_data.to_dict()
    
    def is_interview_complete(self):
        return self.current_question_index >= len(self.interview_data.questions)
    
    def get_question_count(self):
        return len(self.interview_data.questions)