# HR Management Portal

**Assignment 3: End-to-End Portal Design**

**Team:** Mirza Sherafgan Baig (25L-5273) and Taimour Rasheed Awan (25L-5138)

A complete HR portal where employees can request leaves and upload documents, and HR can make announcements, approve leaves, and generate reports.

## Features

### Employees
- Login / Logout
- Request leave (with date validation)
- Upload documents
- View personal leave history
- View company announcements

### HR / Admin
- Approve or reject leave requests
- Post announcements
- View all uploaded documents
- Generate reports (pending leaves, documents, announcements)
- Add new employees

## Technical Requirements Met

| Requirement | How It's Implemented |
|-------------|----------------------|
| Modular programming (`def`) | `user_login()`, `add_record()`, `search_records()`, `generate_report()`, etc. |
| Loops (`for`, `while`) | `while True` main menu + `for` loops for searching and displaying data |
| File handling | JSON files (`employees.json`, `leaves.json`, `documents.json`, `announcements.json`) |
| Exception handling | `try-except` for `FileNotFoundError`, `PermissionError`, `ValueError`, `JSONDecodeError` |
| Documentation | This README + detailed notebook markdown |

## Project Structure

```
hr_portal/
├── hr_portal.ipynb      # Jupyter Notebook (main submission file)
├── app.py               # Streamlit frontend (optional)
├── requirements.txt
├── data/                # JSON data files (created automatically)
│   ├── employees.json
│   ├── leaves.json
│   ├── documents.json
│   └── announcements.json
└── docs/                # Uploaded documents (Streamlit only)
```

## How to Run

### 1. Console Version (Notebook)
```bash
jupyter notebook hr_portal.ipynb
```
- Run all cells
- Uncomment `main()` in the last code cell to start the interactive portal

### 2. Streamlit Frontend
```bash
pip install -r requirements.txt
streamlit run app.py
```

### Demo Credentials
| Role | Username | Password |
|------|----------|----------|
| HR | `hr_admin` | `admin123` |
| Employee | `emp_ali` | `emp123` |
| Employee | `emp_sara` | `emp123` |

## Data Persistence
All data is stored in JSON files inside the `data/` folder. The portal reads existing data on startup and writes updates immediately.

## Document Uploads
- **Console version:** records document metadata only (filename and description).
- **Streamlit version:** stores the actual uploaded file in the `docs/` folder and records its path.

## Known Limitations
- Passwords are stored in plain text (acceptable for a demo, not for production).
- No duplicate-username check when adding employees.
- The console "Add Employee" option does not validate the role value.
- In the console leave approval prompt, any input other than `A` is treated as a rejection.

## Authors
Written by Mirza Sherafgan Baig (25L-5273) and Taimour Rasheed Awan (25L-5138) for Assignment 3.
