# CampusHub 🎓

CampusHub is a student-focused web platform that brings college opportunities, events, internships, hackathons, workshops, webinars, and career resources together in one place.

The project is designed to help students discover opportunities, save useful opportunities, manage their profiles, and explore campus events through a simple and user-friendly interface.

---

## 🚀 Features

### 👤 Student Authentication
- Student signup
- Student login
- Password protection
- Login session using localStorage

### 🧑‍🎓 Student Profile
- View profile
- Edit profile
- College information
- Branch
- Year
- Skills

### 💼 Opportunities
- Browse opportunities
- Search opportunities
- Filter by category
- Post new opportunities
- Apply using external application links

### 🔖 Bookmarks
- Save opportunities
- View saved opportunities
- Remove saved opportunities
- Saved opportunities remain stored in the database

### 📅 Events
- Browse college events
- Search events
- Filter events by category
- Add new events
- Registration links

### 🛡️ Validation
- Form validation
- Email validation
- URL validation
- Required field validation
- Backend validation

### 📱 Responsive Design
- Desktop-friendly interface
- Mobile-friendly layouts
- Responsive cards and forms
- Interactive buttons and navigation

---

## 🛠️ Technologies Used

### Frontend
- HTML5
- CSS3
- JavaScript

### Backend
- Python
- Flask
- Flask-CORS

### Database
- SQLite

### Development Tools
- Visual Studio Code
- Git
- GitHub

---

## 📂 Project Structure

```text
CampusHub/
│
├── css/
│   └── style.css
│
├── js/
│   └── script.js
│
├── assets/
│
├── backend/
│   ├── app.py
│   ├── database.py
│   ├── signup.html
│   └── login.html
│
├── index.html
├── dashboard.html
├── profile.html
├── post.html
├── opportunities.html
├── events.html
├── add-event.html
├── saved.html
│
├── campushub.db
└── README.md