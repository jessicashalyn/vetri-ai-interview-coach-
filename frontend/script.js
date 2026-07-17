let currentQuestionIndex = 0;
let totalQuestions = 0;
let sessionId = 'session_' + Date.now();
let interviewData = null;
let questionHistory = [];
let isInterviewComplete = false;

// DOM Elements
const homePage = document.getElementById('homePage');
const dashboardPage = document.getElementById('dashboardPage');
const profilePage = document.getElementById('profilePage');
const navLinks = document.querySelectorAll('.nav-links a');

const inputForm = document.getElementById('inputForm');
const interviewSection = document.getElementById('interviewSection');
const reportSection = document.getElementById('reportSection');
const interviewForm = document.getElementById('interviewForm');
const currentQuestion = document.getElementById('currentQuestion');
const currentQuestionNum = document.getElementById('currentQuestionNum');
const answerInput = document.getElementById('answerInput');
const submitAnswer = document.getElementById('submitAnswer');
const evaluationResult = document.getElementById('evaluationResult');
const progressBar = document.getElementById('progressBar');
const questionCounter = document.getElementById('questionCounter');
const resetInterview = document.getElementById('resetInterview');
const copyReport = document.getElementById('copyReport');
const downloadPDF = document.getElementById('downloadPDF');

// Navigation
navLinks.forEach(link => {
    link.addEventListener('click', function(e) {
        e.preventDefault();
        const page = this.dataset.page;
        
        navLinks.forEach(l => l.classList.remove('active'));
        this.classList.add('active');
        
        document.querySelectorAll('.page-content').forEach(p => p.style.display = 'none');
        
        if (page === 'home') {
            homePage.style.display = 'block';
        } else if (page === 'dashboard') {
            dashboardPage.style.display = 'block';
            updateDashboard();
        } else if (page === 'profile') {
            profilePage.style.display = 'block';
            updateProfile();
        }
    });
});

// Form submission
interviewForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = {
        full_name: document.getElementById('fullName').value,
        job_role: document.getElementById('jobRole').value,
        experience_level: document.getElementById('experienceLevel').value,
        skills: document.getElementById('skills').value.split(',').map(s => s.trim()),
        interview_type: document.getElementById('interviewType').value,
        difficulty_level: document.getElementById('difficultyLevel').value,
        number_of_questions: parseInt(document.getElementById('numberOfQuestions').value),
        session_id: sessionId
    };
    
    localStorage.setItem('interviewData', JSON.stringify(formData));
    interviewData = formData;
    totalQuestions = formData.number_of_questions;
    
    try {
        const response = await fetch('/api/start_interview', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            inputForm.style.display = 'none';
            interviewSection.style.display = 'block';
            
            // Show first question
            displayQuestion(data.question);
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        alert('Error starting interview: ' + error.message);
    }
});

// Display question
function displayQuestion(questionData) {
    if (questionData && !questionData.complete) {
        currentQuestion.textContent = questionData.question;
        currentQuestionNum.textContent = questionData.index;
        currentQuestionIndex = questionData.index;
        
        answerInput.value = '';
        evaluationResult.style.display = 'none';
        submitAnswer.style.display = 'flex';
        
        // Update progress
        const progress = ((questionData.index - 1) / totalQuestions) * 100;
        progressBar.style.width = progress + '%';
        questionCounter.textContent = `${questionData.index} of ${totalQuestions}`;
    } else {
        generateReport();
    }
}

// Submit answer and get next question
submitAnswer.addEventListener('click', async () => {
    const answer = answerInput.value.trim();
    if (!answer) {
        alert('Please enter your answer before submitting.');
        return;
    }
    
    const question = currentQuestion.textContent;
    
    try {
        const response = await fetch('/api/submit_answer', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_id: sessionId,
                question: question,
                answer: answer
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Save to question history
            questionHistory.push({
                question: question,
                answer: answer,
                score: data.evaluation.score,
                feedback: data.evaluation.feedback
            });
            localStorage.setItem('questionHistory', JSON.stringify(questionHistory));
            
            // Display evaluation with score
            displayEvaluation(data.evaluation);
            submitAnswer.style.display = 'none';
            
            // Update progress after submission
            const progress = (currentQuestionIndex / totalQuestions) * 100;
            progressBar.style.width = progress + '%';
            
            // Check if interview is complete
            isInterviewComplete = data.is_complete;
            
            if (isInterviewComplete) {
                // Show completion message and generate report
                setTimeout(() => {
                    generateReport();
                }, 2000);
            } else {
                // Auto fetch next question after evaluation
                setTimeout(() => {
                    fetchNextQuestion();
                }, 1500);
            }
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        alert('Error submitting answer: ' + error.message);
    }
});

// Fetch next question automatically
async function fetchNextQuestion() {
    try {
        const response = await fetch('/api/get_next_question', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_id: sessionId
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            if (data.complete) {
                generateReport();
            } else {
                displayQuestion(data.question);
            }
        } else {
            alert('Error fetching next question: ' + data.error);
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

// Display evaluation with score
function displayEvaluation(evaluation) {
    // Display score with animation
    const scoreElement = document.getElementById('questionScore');
    scoreElement.textContent = evaluation.score;
    
    // Color based on score
    if (evaluation.score >= 80) {
        scoreElement.style.color = '#00d2ff';
    } else if (evaluation.score >= 60) {
        scoreElement.style.color = '#ffa500';
    } else {
        scoreElement.style.color = '#ff6b6b';
    }
    
    document.getElementById('feedbackText').textContent = evaluation.feedback || 'No feedback provided';
    document.getElementById('strengthsText').textContent = evaluation.strengths || 'No strengths listed';
    document.getElementById('improvementsText').textContent = evaluation.improvements || 'No improvements suggested';
    document.getElementById('suggestedAnswer').textContent = evaluation.suggested_answer || 'No suggested answer provided';
    document.getElementById('skillsToImprove').textContent = evaluation.skills_to_improve || 'No skills to improve listed';
    document.getElementById('learningTopics').textContent = evaluation.learning_topics || 'No learning topics recommended';
    
    evaluationResult.style.display = 'block';
    evaluationResult.scrollIntoView({ behavior: 'smooth' });
}

// Generate final report
async function generateReport() {
    try {
        const response = await fetch('/api/get_report', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_id: sessionId
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            interviewSection.style.display = 'none';
            reportSection.style.display = 'block';
            
            document.getElementById('overallScore').textContent = data.overall_score;
            document.getElementById('reportText').innerHTML = formatReport(data.report);
            
            // Update dashboard and profile
            updateDashboard();
            updateProfile();
        } else {
            alert('Error generating report: ' + data.error);
        }
    } catch (error) {
        alert('Error generating report: ' + error.message);
    }
}

// Format report with HTML
function formatReport(reportText) {
    const lines = reportText.split('\n');
    let html = '';
    let inList = false;
    
    for (let line of lines) {
        line = line.trim();
        if (!line) {
            if (inList) {
                html += '</ul>';
                inList = false;
            }
            continue;
        }
        
        if (line.match(/^\d+\./)) {
            if (inList) {
                html += '</ul>';
                inList = false;
            }
            html += `<h3>${line}</h3>`;
        } else if (line.startsWith('•') || line.startsWith('-')) {
            if (!inList) {
                html += '<ul>';
                inList = true;
            }
            html += `<li>${line.substring(1).trim()}</li>`;
        } else {
            if (inList) {
                html += '</ul>';
                inList = false;
            }
            html += `<p>${line}</p>`;
        }
    }
    
    if (inList) {
        html += '</ul>';
    }
    
    return html;
}

// Copy Report
copyReport.addEventListener('click', () => {
    const reportText = document.getElementById('reportText').innerText;
    const overallScore = document.getElementById('overallScore').textContent;
    const fullReport = `📊 Vetri AI Interview Report\n\nOverall Score: ${overallScore}/100\n\n${reportText}`;
    
    navigator.clipboard.writeText(fullReport).then(() => {
        alert('✅ Report copied to clipboard!');
    }).catch(() => {
        const textarea = document.createElement('textarea');
        textarea.value = fullReport;
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
        alert('✅ Report copied to clipboard!');
    });
});

// Download Full Report as PDF
downloadPDF.addEventListener('click', () => {
    const reportElement = document.getElementById('reportSection');
    
    // Get all data
    const overallScore = document.getElementById('overallScore').textContent;
    const reportText = document.getElementById('reportText').innerHTML;
    const interviewData = JSON.parse(localStorage.getItem('interviewData') || '{}');
    const questionHistory = JSON.parse(localStorage.getItem('questionHistory') || '[]');
    
    // Create full report HTML
    const fullReportHTML = `
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Interview Report - ${interviewData.full_name || 'Candidate'}</title>
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body { font-family: Arial, sans-serif; padding: 40px; background: white; }
                .report-header { text-align: center; padding: 30px; border-bottom: 3px solid #6C63FF; margin-bottom: 30px; }
                .report-header h1 { color: #6C63FF; font-size: 28px; }
                .report-header p { color: #666; margin-top: 5px; }
                .score-section { text-align: center; padding: 30px; background: linear-gradient(135deg, #667eea, #764ba2); border-radius: 15px; margin: 20px 0; color: white; }
                .score-section .score { font-size: 72px; font-weight: bold; }
                .score-section .label { font-size: 18px; opacity: 0.9; }
                .info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin: 20px 0; }
                .info-item { background: #f8f8fe; padding: 15px; border-radius: 10px; }
                .info-item label { font-weight: bold; color: #666; display: block; font-size: 12px; text-transform: uppercase; }
                .info-item p { margin-top: 5px; color: #333; font-size: 16px; }
                .report-content { margin: 30px 0; }
                .report-content h3 { color: #6C63FF; margin: 20px 0 10px 0; }
                .report-content p { line-height: 1.8; color: #444; margin-bottom: 10px; }
                .report-content ul { list-style: none; padding: 0; }
                .report-content ul li { padding: 8px 0 8px 25px; position: relative; color: #444; }
                .report-content ul li:before { content: "▸"; position: absolute; left: 0; color: #6C63FF; }
                .footer { text-align: center; padding: 20px; margin-top: 30px; border-top: 1px solid #ddd; color: #999; font-size: 12px; }
                .question-history { margin: 20px 0; }
                .question-item { background: #f8f8fe; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 4px solid #6C63FF; }
                .question-item .q-text { font-weight: bold; color: #333; }
                .question-item .q-score { color: #6C63FF; font-weight: bold; margin-top: 5px; }
                .question-item .q-feedback { color: #666; margin-top: 5px; font-size: 14px; }
            </style>
        </head>
        <body>
            <div class="report-header">
                <h1>🎯 Vetri AI Interview Report</h1>
                <p>Generated on: ${new Date().toLocaleString()}</p>
            </div>
            
            <div class="info-grid">
                <div class="info-item">
                    <label>Candidate Name</label>
                    <p>${interviewData.full_name || 'Not specified'}</p>
                </div>
                <div class="info-item">
                    <label>Job Role</label>
                    <p>${interviewData.job_role || 'Not specified'}</p>
                </div>
                <div class="info-item">
                    <label>Experience Level</label>
                    <p>${interviewData.experience_level || 'Not specified'}</p>
                </div>
                <div class="info-item">
                    <label>Skills</label>
                    <p>${interviewData.skills ? interviewData.skills.join(', ') : 'Not specified'}</p>
                </div>
                <div class="info-item">
                    <label>Interview Type</label>
                    <p>${interviewData.interview_type || 'Not specified'}</p>
                </div>
                <div class="info-item">
                    <label>Difficulty Level</label>
                    <p>${interviewData.difficulty_level || 'Not specified'}</p>
                </div>
            </div>
            
            <div class="score-section">
                <div class="label">Overall Score</div>
                <div class="score">${overallScore}/100</div>
            </div>
            
            <div class="question-history">
                <h3 style="color: #6C63FF; margin-bottom: 15px;">Question-wise Breakdown</h3>
                ${questionHistory.map((q, i) => `
                    <div class="question-item">
                        <div class="q-text">Q${i+1}: ${q.question}</div>
                        <div class="q-score">Score: ${q.score || 0}/100</div>
                        <div class="q-feedback">${q.feedback || ''}</div>
                    </div>
                `).join('')}
            </div>
            
            <div class="report-content">
                ${reportText}
            </div>
            
            <div class="footer">
                <p>© 2026 Vetri AI Interview Coach. Powered by Google Gemini AI</p>
            </div>
        </body>
        </html>
    `;
    
    // Open new window for printing
    const printWindow = window.open('', '_blank');
    printWindow.document.write(fullReportHTML);
    printWindow.document.close();
    
    // Wait for content to load then print
    setTimeout(() => {
        printWindow.print();
    }, 500);
    
    // Alternative: Download as PDF using html2pdf
    // Show loading
    downloadPDF.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating PDF...';
    downloadPDF.disabled = true;
    
    // Create temporary container
    const tempContainer = document.createElement('div');
    tempContainer.innerHTML = fullReportHTML;
    tempContainer.style.position = 'absolute';
    tempContainer.style.left = '-9999px';
    tempContainer.style.top = '0';
    tempContainer.style.width = '794px';
    tempContainer.style.background = 'white';
    tempContainer.style.padding = '40px';
    document.body.appendChild(tempContainer);
    
    // Use html2pdf
    const opt = {
        margin: 10,
        filename: `Interview_Report_${interviewData.full_name || 'Candidate'}_${new Date().toISOString().split('T')[0]}.pdf`,
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2, useCORS: true },
        jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
    };
    
    html2pdf().set(opt).from(tempContainer).save().then(() => {
        document.body.removeChild(tempContainer);
        downloadPDF.innerHTML = '<i class="fas fa-file-pdf"></i> Download Full Report as PDF';
        downloadPDF.disabled = false;
    });
});

// Reset Interview
resetInterview.addEventListener('click', () => {
    if (confirm('Are you sure you want to reset everything?')) {
        localStorage.removeItem('interviewData');
        localStorage.removeItem('questionHistory');
        questionHistory = [];
        interviewData = null;
        sessionId = 'session_' + Date.now();
        isInterviewComplete = false;
        
        reportSection.style.display = 'none';
        inputForm.style.display = 'block';
        interviewSection.style.display = 'none';
        document.getElementById('interviewForm').reset();
        
        progressBar.style.width = '0%';
        questionCounter.textContent = '0 of 0';
        
        document.querySelectorAll('.page-content').forEach(p => p.style.display = 'none');
        homePage.style.display = 'block';
        navLinks.forEach(l => l.classList.remove('active'));
        document.querySelector('[data-page="home"]').classList.add('active');
        
        updateDashboard();
        updateProfile();
    }
});

// Update Dashboard
function updateDashboard() {
    const history = JSON.parse(localStorage.getItem('questionHistory') || '[]');
    const data = JSON.parse(localStorage.getItem('interviewData') || '{}');
    
    document.getElementById('totalQuestions').textContent = data.number_of_questions || 0;
    document.getElementById('answeredQuestions').textContent = history.length || 0;
    
    if (history.length > 0) {
        const avgScore = history.reduce((sum, h) => sum + (h.score || 0), 0) / history.length;
        document.getElementById('averageScore').textContent = Math.round(avgScore) + '%';
        document.getElementById('completionRate').textContent = 
            Math.round((history.length / (data.number_of_questions || 1)) * 100) + '%';
    } else {
        document.getElementById('averageScore').textContent = '0%';
        document.getElementById('completionRate').textContent = '0%';
    }
    
    const historyContainer = document.getElementById('questionHistory');
    if (history.length > 0) {
        let html = '';
        history.forEach((item, index) => {
            html += `
                <div class="question-history-item">
                    <div class="q-text">Q${index + 1}: ${item.question}</div>
                    <div class="q-score">Score: ${item.score || 0}/100</div>
                </div>
            `;
        });
        historyContainer.innerHTML = html;
    } else {
        historyContainer.innerHTML = '<p class="no-data">No interview data available. Start an interview to see history.</p>';
    }
}

// Update Profile
function updateProfile() {
    const data = JSON.parse(localStorage.getItem('interviewData') || '{}');
    const history = JSON.parse(localStorage.getItem('questionHistory') || '[]');
    
    document.getElementById('profileName').textContent = data.full_name ? `${data.full_name}'s Profile` : 'User Profile';
    document.getElementById('profileRole').textContent = data.job_role ? `Job Role: ${data.job_role}` : 'Job Role: Not Set';
    
    document.getElementById('profileFullName').textContent = data.full_name || 'Not set';
    document.getElementById('profileJobRole').textContent = data.job_role || 'Not set';
    document.getElementById('profileExperience').textContent = data.experience_level || 'Not set';
    document.getElementById('profileSkills').textContent = data.skills ? data.skills.join(', ') : 'Not set';
    document.getElementById('profileInterviewType').textContent = data.interview_type || 'Not set';
    document.getElementById('profileDifficulty').textContent = data.difficulty_level || 'Not set';
    document.getElementById('profileQuestions').textContent = data.number_of_questions || 'Not set';
    
    if (history.length > 0) {
        const avgScore = history.reduce((sum, h) => sum + (h.score || 0), 0) / history.length;
        document.getElementById('profileOverallScore').textContent = Math.round(avgScore) + '%';
        document.getElementById('profileAnswered').textContent = history.length;
    } else {
        document.getElementById('profileOverallScore').textContent = '0%';
        document.getElementById('profileAnswered').textContent = '0';
    }
}

// Auto-resize textarea
answerInput.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = this.scrollHeight + 'px';
});

// Initialize dashboard and profile on load
document.addEventListener('DOMContentLoaded', () => {
    updateDashboard();
    updateProfile();
});

// Add at the top of script.js
console.log('Vetri AI Interview Coach - Starting...');

// Add this inside the form submission
interviewForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    console.log('Form submitted');
    // ... rest of your code
});

// Add this inside displayQuestion function
function displayQuestion(questionData) {
    console.log('Displaying question:', questionData);
    // ... rest of your code
}

// Display question with clean formatting
function displayQuestion(questionData) {
    if (questionData && !questionData.complete) {
        // Clean the question text
        let questionText = questionData.question;
        // Remove any "Question X:" prefix if present
        questionText = questionText.replace(/^Question\s*\d+[:.]\s*/i, '');
        questionText = questionText.replace(/^\d+[:.]\s*/, '');
        
        currentQuestion.textContent = questionText;
        currentQuestionNum.textContent = questionData.index;
        currentQuestionIndex = questionData.index;
        
        answerInput.value = '';
        evaluationResult.style.display = 'none';
        submitAnswer.style.display = 'flex';
        
        // Update progress
        const progress = ((questionData.index - 1) / totalQuestions) * 100;
        progressBar.style.width = progress + '%';
        questionCounter.textContent = `${questionData.index} of ${totalQuestions}`;
        
        console.log(`📝 Showing Question ${questionData.index}: ${questionText}`);
    } else {
        generateReport();
    }
}

// Fetch next question automatically
async function fetchNextQuestion() {
    try {
        const response = await fetch('/api/get_next_question', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_id: sessionId
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            if (data.complete) {
                console.log('✅ Interview complete! Generating report...');
                generateReport();
            } else {
                console.log(`📝 Next question: ${data.question.question}`);
                displayQuestion(data.question);
            }
        } else {
            alert('Error fetching next question: ' + data.error);
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}