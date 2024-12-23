# 🌟 Jobily - Job Board Platform

## 🖋️ Project Description
Jobily is a modern job board platform built with Django REST Framework. It connects employers and job seekers through features like job posting, application management, and profile customization.

## 🛠️ Tech Stack
- **Backend:** Django 4.2, Django REST Framework  
- **Database:** PostgreSQL  
- **Caching:** Redis  
- **Task Queue:** Celery  
- **Authentication:** JWT (JSON Web Tokens)  
- **API Documentation:** Django REST Swagger/OpenAPI  
- **File Storage:** Django Storage (AWS S3)  

---

## 🚀 Core Features

### 👤 User Management
- Two user types: Employers and Job Seekers  
- Custom authentication system  
- Profile management with file uploads  
- Skills management  

### 💼 Company Management
- Company profiles and verification  
- Multiple employer accounts per company  
- Statistics and analytics  
- Company search and filtering  

### 📋 Job Management
- Enhanced job posting system  
- Job search with advanced filters  
- Application management  
- Automatic job expiration  
- Recommended similar jobs  

### 📊 Analytics & Features
- Real-time statistics  
- Email notifications  
- Caching system  
- Asynchronous tasks  
- OpenAI integration for profile generation  

---

## 📚 API Documentation

### 🔐 Authentication Endpoints
**Registration:**  
- Employer: `POST /api/auth/register/employer/`  
- Job Seeker: `POST /api/auth/register/job-seeker/`  
- Swagger Documentation: `GET /api/docs/`
- Redoc Documentation: `GET /api/docs/redoc/`

**Login:**  
- Endpoint: `POST /api/auth/login/`  

---

### 👥 Accounts API

**Job Seeker Profile:**  
- `GET /api/accounts/jobseeker/me/` - Retrieve own profile  
- `PUT /api/accounts/jobseeker/me/` - Update profile  
- `POST /api/accounts/jobseeker/me/` - Create profile  
- `GET /api/accounts/jobseeker/statistics/` - Profile statistics  

**Skills Management:**  
- `GET /api/accounts/skills/` - List of skills  
- `POST /api/accounts/skills/add_skills/` - Add skills to profile  
- `POST /api/accounts/skills/remove_skills/` - Remove skills from profile  
- `GET /api/accounts/skills/by_category/` - Skills by category  

**Education & Experience:**  
- `GET /api/accounts/education/` - Education records  
- `POST /api/accounts/education/` - Add education record  
- `GET /api/accounts/experience/` - Work experience  
- `POST /api/accounts/experience/` - Add work experience  

---

### 💼 Companies API

**Company Management:**  
- `POST /api/companies/register/` - Register new company  
- `GET /api/companies/` - List of companies  
- `GET /api/companies/{id}/` - Company details  
- `PUT /api/companies/{id}/` - Update company  
- `GET /api/companies/me/` - Own company  
- `GET /api/companies/filters/` - Filter options  

---

### 💼 Jobs API

**Job Postings:**  
- `GET /api/jobs/` - List of jobs  
- `POST /api/jobs/` - Add new job  
- `GET /api/jobs/{id}/` - Job details  
- `PUT /api/jobs/{id}/` - Update job  
- `DELETE /api/jobs/{id}/` - Delete job  
- `POST /api/jobs/{id}/apply/` - Apply to job  
- `GET /api/jobs/my_jobs/` - Own jobs  
- `GET /api/jobs/similar_jobs/{id}/` - Similar jobs  
- `GET /api/jobs/statistics/` - Job statistics  

---

## 🚀 Setup & Installation

1. **Clone repository:**
   ```bash
   git clone https://github.com/yourusername/jobily.git
   cd jobily
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   
   pip install -r requirements.txt 
   ```

3. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

4. **Run server:**
      ```bash 
      python manage.py runserver  
      ```
      
