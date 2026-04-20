# 🏨 HMC Hostel Booking & Management System

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.2.5-000000?style=for-the-badge&logo=flask&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Ready-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![Power BI](https://img.shields.io/badge/Power_BI-Integrated-F2C811?style=for-the-badge&logo=powerbi&logoColor=black)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

A professional, cloud-ready Flask web application designed for DIAT Pune to manage hostel registrations, guest check-ins, and real-time occupancy analytics.

---

## 🚀 Key Features

- **🎓 Student Registration:** Simple and intuitive form for hostel room requests.
- **👑 Admin Dashboard:** Complete control over applications (Approve/Reject/Delete).
- **🚪 Check-In/Check-Out System:** Track live occupancy with a single click.
- **📧 Automated Emails:** Instant notifications for approvals and rejections.
- **📊 Power BI Analytics:** Built-in dashboard for live data visualization and reporting.
- **🐘 Database Flexibility:** Seamlessly switches between **SQLite** (Local) and **PostgreSQL** (Production).

---

## 🛠️ Tech Stack

- **Backend:** Python (Flask)
- **Frontend:** HTML5, CSS3 (Vanilla CSS)
- **Database:** PostgreSQL (Cloud) / SQLite (Local)
- **Analytics:** Microsoft Power BI
- **Deployment:** Render / Railway / Heroku

---

## 💻 Local Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/LEVELING2108/ACCOMODATION_hmc-hostel-system.git
   cd -hmc-hostel-system-
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```
   Open `http://127.0.0.1:5000` in your browser.

---

## ☁️ Cloud Deployment (Production)

### Phase 1: Database Setup
1. Create a **PostgreSQL** database on Render or Railway.
2. Copy the **External DATABASE_URL**.

### Phase 2: Web Service Setup
1. Connect this GitHub repository to your cloud provider.
2. Add the following **Environment Variables**:
   - `DATABASE_URL`: (Paste your PostgreSQL URL)
   - `FLASK_SECRET_KEY`: `hmc-hostel-secret-key-2026`
   - `EMAIL_PASSWORD`: (Your Gmail App Password for notifications)

---

## 📈 Power BI Integration

1. Connect Power BI Desktop to your Cloud PostgreSQL database.
2. Create your dashboard and click **Publish to Web**.
3. Copy the **Embed Link**.
4. Paste the link into `templates/admin_dashboard.html` at the `<iframe>` section (Line 177).

---

## 🔒 Default Credentials (Admin)
- **Username:** `admin`
- **Password:** `admin123`

---
*Developed for DIAT Pune Hostel Management Committee (HMC).*
