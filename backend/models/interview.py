class InterviewData:
    def __init__(self):
        self.full_name = ""
        self.job_role = ""
        self.experience_level = ""
        self.skills = []
        self.interview_type = ""
        self.difficulty_level = ""
        self.number_of_questions = 0
        self.questions = []
        self.answers = []
        self.evaluations = []
    
    def to_dict(self):
        return {
            "full_name": self.full_name,
            "job_role": self.job_role,
            "experience_level": self.experience_level,
            "skills": self.skills,
            "interview_type": self.interview_type,
            "difficulty_level": self.difficulty_level,
            "number_of_questions": self.number_of_questions,
            "questions": self.questions,
            "answers": self.answers,
            "evaluations": self.evaluations
        }