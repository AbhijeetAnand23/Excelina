# Excelina - AI-Powered Excel Interviewer

Excelina is a full-stack web application that simulates an AI-powered Excel interview experience. It presents Excel-related questions, evaluates user responses using LLM-based techniques, and provides skill-specific feedback. It is intended to help users prepare for real Excel-based interviews in an interactive and intelligent way.

## 🚀 Live Demos

- **Frontend (Netlify)**: [https://excelina.netlify.app](https://excelina.netlify.app)
- **Backend (Hugging Face Spaces)**: [https://huggingface.co/spaces/AbhijeetAnand30/excelina-backend](https://huggingface.co/spaces/AbhijeetAnand30/excelina-backend)

---

## 🛠️ Tech Stack

**Frontend:** Angular 17, SCSS, SweetAlert2  
**Backend:** Flask, Flask-CORS, PyMongo, JWT, Bcrypt  
**Database:** MongoDB Atlas (NoSQL, cloud-hosted)  
**Deployment:** Netlify (frontend), Hugging Face Spaces (backend)

---
## 🧠 AI Models & Evaluation Logic

### 🤖 Meta-LLaMA-3 70B Instruct

The backbone of Excelina's intelligence is Meta's **LLaMA-3 70B Instruct** model, powering multiple key functionalities throughout the interview process:

1. **📚 Question Generation**  
   - Starts with a curated **seed set** of Excel interview questions.
   - Based on the user's role (beginner or experienced), level, and previous responses, LLaMA-3 dynamically generates new, increasingly tailored questions.
   - This creates a **self-reinforcing question bank** that evolves with user participation.

2. **📝 Feedback Generation**  
   - After each response, LLaMA-3 provides **AI-powered feedback** including:
     - Whether the answer is correct, partially correct, or incorrect.
     - Explanations and insights into the Excel concept being tested.
     - Suggestions for improvement and next steps.

3. **🧼 Toxicity & Language Moderation**  
   - LLaMA-3 is prompt-engineered to also function as a **toxicity filter**.
   - All user responses are screened for **offensive, inappropriate, or harmful language**.
   - Ensures a safe, respectful, and professional experience for all users.



### 📊 DeepEval (GEval)

Excelina uses **DeepEval's GEval framework** to rigorously evaluate the quality of user responses:

- ✅ **Relevance**: Is the answer aligned with what was asked?
- 🎯 **Accuracy**: Does the response produce the correct result or logic?
- 📦 **Completeness**: Are all parts of the question addressed?

These scores directly influence the correctness tag, AI feedback, and user progress tracking.

---
## ✨ Features

- 🧠 **LLM-Powered Engine**: Uses Meta LLaMA-3 for dynamic question generation, real-time feedback, and toxicity filtering.
- 📄 **Downloadable Reports**: Get a detailed interview report with skill-wise analysis and AI-generated feedback.
- 📊 **Level-Based Progression**: Adaptive difficulty and scoring with instant evaluation.
- 🔁 **Auto-Expanding Question Bank**: More users = smarter, richer question pool.
- 🌐 **RESTful API Backend**: Clean, scalable Flask APIs power the frontend.
- 🗂️ **MongoDB Tracking**: Stores user sessions and interview history efficiently.
- 🔐 **JWT Authentication**: Secure login with password protection and token-based access.
- 🚀 **Deployed on Netlify + Hugging Face**: Angular frontend + Flask backend fully live.



---

## 📦 Project Structure

```
Excelina/
├── frontend/                  # Angular application
│   ├── src/
│   │   └── app/               # Components, services, routing
│   └── dist/frontend/browser/ # Production build output
├── backend/                   # Flask API
│   ├── app/                   # answer_engine, interview_engine, routes
│   ├── data/                  # MongoDB connection setup
│   └── app.py                 # Entry point
└── .github/workflows/         # CI/CD YAML for Hugging Face deploy
```

---

## 🧑‍💻 Installation & Setup

### Prerequisites
- Node.js & Angular CLI
- Python 3.9+
- MongoDB Atlas Cluster
- Git

### Clone Repository
```bash
git clone https://github.com/your-username/excelina.git
cd excelina
```

### Setup Frontend
```bash
cd frontend
npm install
ng serve
```

### Setup Backend
```bash
cd backend
pip install -r requirements.txt
python app.py
```

### Environment Variables

In `backend`, create a `.env` file:

```
MONGO_URI=mongodb+srv://<user>:<pass>@cluster.mongodb.net/excelina
JWT_SECRET=your_jwt_secret_key
```

---

## 🎯 Usage

1. Register/Login as a user.
2. The app assigns Excel questions across 4 levels.
3. User types answers and submits.
4. Backend evaluates answer → scores + feedback.
5. At the end, a feedback summary is shown.

Note: The question set evolves automatically as more users interact — newly generated LLaMA-based questions are stored and reused in future interviews.

---

## 🔗 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST   | `/register` | Register a new user |
| POST   | `/login`    | Login and receive JWT |
| POST   | `/start`    | Begin new interview |
| POST   | `/submit_answer` | Submit an answer |
| GET    | `/feedback/:userId` | Get full interview result |


---

## 💡 Future Suggestions & Enhancements

- **Voice-based input** for accessibility
- **Admin dashboard** to view top users, question stats, feedback analytics
- **Question tagging** (by topic like charts, pivot tables, etc.)
- **Dynamic difficulty tuning** based on user performance
- **LLM fine-tuning** on a dataset of real Excel interviews for hyper-targeted feedback
- **Gamification**: Leaderboards, badges, progress bars

---