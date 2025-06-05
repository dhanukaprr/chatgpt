# Membership and Loan Web App

This is a simple Flask application providing a basic membership and loan management system. Institutions can register employees, record membership fees and loan instalments, and manage loan applications.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Initialize the database:
   ```bash
   flask --app app.py init-db
   ```
3. Run the development server:
   ```bash
   flask --app app.py run
   ```

The site will be available at `http://127.0.0.1:5000/`.
