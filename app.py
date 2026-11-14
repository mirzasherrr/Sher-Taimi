"""
HR Management Portal - Streamlit Frontend
Supports employee document upload, leave requests, and HR announcements.
Shares data with the console backend via JSON files.
Run with: streamlit run app.py
"""

import streamlit as st
import json
import os
from datetime import datetime
import shutil

# File paths
DATA_DIR = "data"
DOCS_DIR = "docs"
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(DOCS_DIR, exist_ok=True)

EMPLOYEES_FILE = os.path.join(DATA_DIR, "employees.json")
LEAVES_FILE = os.path.join(DATA_DIR, "leaves.json")
DOCUMENTS_FILE = os.path.join(DATA_DIR, "documents.json")
ANNOUNCEMENTS_FILE = os.path.join(DATA_DIR, "announcements.json")

# ========== Core Backend Functions ==========

def load_data(filename):
    """Load JSON data with robust error handling."""
    try:
        if not os.path.exists(filename):
            return []
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        st.error(f"Error: Corrupt data in {filename}")
        return []
    except PermissionError:
        st.error(f"Permission denied reading {filename}")
        return []
    except Exception as e:
        st.error(f"Unexpected error loading {filename}: {e}")
        return []

def save_data(filename, data):
    """Save data to JSON with error handling."""
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
        return True
    except PermissionError:
        st.error(f"Permission denied writing to {filename}")
        return False
    except Exception as e:
        st.error(f"Error saving {filename}: {e}")
        return False

def initialize_sample_data():
    """Create sample employees if none exist."""
    if not os.path.exists(EMPLOYEES_FILE):
        sample = [
            {
                "id": 1,
                "username": "hr_admin",
                "password": "admin123",
                "name": "Sarah Khan",
                "role": "HR",
                "department": "Human Resources",
                "email": "hr@company.com"
            },
            {
                "id": 2,
                "username": "emp_ali",
                "password": "emp123",
                "name": "Ali Ahmed",
                "role": "Employee",
                "department": "Engineering",
                "email": "ali@company.com"
            },
            {
                "id": 3,
                "username": "emp_sara",
                "password": "emp123",
                "name": "Sara Malik",
                "role": "Employee",
                "department": "Marketing",
                "email": "sara@company.com"
            }
        ]
        save_data(EMPLOYEES_FILE, sample)
    
    for f in [LEAVES_FILE, DOCUMENTS_FILE, ANNOUNCEMENTS_FILE]:
        if not os.path.exists(f):
            save_data(f, [])

def user_login(username, password):
    """Authenticate user. Returns user dict or None."""
    employees = load_data(EMPLOYEES_FILE)
    for emp in employees:
        if emp["username"] == username and emp["password"] == password:
            return emp
    return None

def add_record(filename, record):
    """Generic add record function."""
    data = load_data(filename)
    # Auto-increment ID
    record["id"] = max([r.get("id", 0) for r in data], default=0) + 1
    data.append(record)
    return save_data(filename, data)

def search_records(filename, key, value):
    """Search records by key-value. Uses for loop as required."""
    data = load_data(filename)
    results = []
    for item in data:
        if str(item.get(key, "")).lower() == str(value).lower():
            results.append(item)
    return results

def generate_report(report_type="pending_leaves"):
    """Generate reports for HR."""
    if report_type == "pending_leaves":
        leaves = load_data(LEAVES_FILE)
        pending = []
        for leave in leaves:
            if leave.get("status") == "Pending":
                pending.append(leave)
        return pending
    elif report_type == "all_documents":
        return load_data(DOCUMENTS_FILE)
    elif report_type == "announcements":
        return load_data(ANNOUNCEMENTS_FILE)
    return []

# Initialize
initialize_sample_data()

# ========== Streamlit UI ==========

st.set_page_config(
    page_title="Sher & Taimi's Co. | HR Portal",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    .stApp { background-color: #f5f7fa; }
    [data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e5e7eb; }
    h1, h2, h3 { color: #111827; font-weight: 600; letter-spacing: -0.02em; }
    .card {
        background: #ffffff; border-radius: 12px; padding: 1.25rem 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06); border: 1px solid #e5e7eb; margin-bottom: 1rem;
    }
    .badge { display: inline-block; padding: 0.25rem 0.75rem; border-radius: 999px; font-size: 0.8rem; font-weight: 600; }
    .badge-pending { background: #fef3c7; color: #92400e; }
    .badge-approved { background: #d1fae5; color: #065f46; }
    .badge-rejected { background: #fee2e2; color: #991b1b; }
    .avatar {
        width: 40px; height: 40px; border-radius: 50%; background: #0d6efd; color: white;
        display: flex; align-items: center; justify-content: center; font-weight: 600;
    }
    .login-box {
        max-width: 440px; margin: 5rem auto; background: white; padding: 2.5rem;
        border-radius: 16px; box-shadow: 0 10px 40px rgba(0,0,0,0.08); border: 1px solid #e5e7eb;
    }
    .empty-state { text-align: center; padding: 3rem 1rem; color: #6b7280; }
    #MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

def get_initials(name):
    parts = name.split()
    return (parts[0][0] + parts[-1][0]).upper() if len(parts) > 1 else name[:2].upper()

def status_badge(status):
    css = {"Pending": "badge-pending", "Approved": "badge-approved", "Rejected": "badge-rejected"}.get(status, "")
    return f'<span class="badge {css}">{status}</span>'

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None
if "notifications" not in st.session_state:
    st.session_state.notifications = []
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

if not st.session_state.logged_in:
    # Center everything using columns
    left, center, right = st.columns([1, 1.2, 1])
    with center:
        st.markdown("<div style='text-align:center; margin-bottom:1rem;'><img src='data:image/jpeg;base64,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' width='120' style='display:block; margin:0 auto;'></div>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align:center; margin:0.3rem 0 0.1rem 0; font-weight:700; letter-spacing:-0.03em;'>Sher & Taimi's Co.</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:#6b7280; margin-bottom:1.8rem; font-size:0.95rem;'>HR Management Portal</p>", unsafe_allow_html=True)
        
        username = st.text_input("Username", placeholder="Enter username", label_visibility="collapsed")
        password = st.text_input("Password", type="password", placeholder="Enter password", label_visibility="collapsed")
        
        if st.button("Sign In", type="primary", use_container_width=True):
            user = user_login(username, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.user = user
                st.rerun()
            else:
                st.error("Invalid credentials")
        
        with st.expander("Demo Accounts"):
            st.markdown("**HR:** `hr_admin` / `admin123`\n\n**Employee:** `emp_ali` / `emp123`")
    st.stop()

user = st.session_state.user

with st.sidebar:
    initials = get_initials(user["name"])
    st.markdown(f'<div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:1rem;"><div class="avatar">{initials}</div><div><strong>{user["name"]}</strong><br><small style="color:#6b7280;">{user["role"]} • {user["department"]}</small></div></div>', unsafe_allow_html=True)
    st.divider()
    dark = st.toggle("Dark Mode", value=st.session_state.dark_mode)
    if dark != st.session_state.dark_mode:
        st.session_state.dark_mode = dark
        st.rerun()
    if st.session_state.dark_mode:
        st.markdown("""<style>.stApp{background:#0f172a;color:#e2e8f0;}[data-testid="stSidebar"]{background:#1e293b;}.card{background:#1e293b;border-color:#334155;color:#e2e8f0;}h1,h2,h3{color:#f1f5f9;}</style>""", unsafe_allow_html=True)
    st.divider()
    if user["role"] == "Employee":
        menu = st.radio("Menu", ["Dashboard", "Request Leave", "Upload Document", "My Leaves", "Announcements", "Calendar"], label_visibility="collapsed")
    else:
        menu = st.radio("Menu", ["Dashboard", "Manage Leaves", "Post Announcement", "View Documents", "Generate Report", "Add Employee", "Calendar"], label_visibility="collapsed")
    st.divider()
    if st.button("Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()

st.markdown("# Sher & Taimi's Co.")
st.caption("HR Management Portal")

if user["role"] == "Employee":
    if menu == "Dashboard":
        st.markdown(f"### Welcome back, {user['name']}")
        my_leaves = search_records(LEAVES_FILE, "employee_id", user["id"])
        total_days = 15
        used = 0
        for l in my_leaves:
            if l.get("status") == "Approved":
                try:
                    s = datetime.strptime(l["start_date"], "%Y-%m-%d")
                    e = datetime.strptime(l["end_date"], "%Y-%m-%d")
                    used += (e - s).days + 1
                except:
                    pass
        remaining = max(0, total_days - used)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Leave Balance", f"{remaining} days")
        c2.metric("Total Requests", len(my_leaves))
        c3.metric("Pending", len([l for l in my_leaves if l.get("status")=="Pending"]))
        c4.metric("Approved", len([l for l in my_leaves if l.get("status")=="Approved"]))
        st.markdown("---")
        st.subheader("Recent Announcements")
        anns = load_data(ANNOUNCEMENTS_FILE)
        if anns:
            for a in reversed(anns[-3:]):
                st.markdown(f'<div class="card"><strong>{a["title"]}</strong><br>{a["content"]}<br><small style="color:#6b7280;">By {a["author"]} • {a["date"]}</small></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="empty-state">No announcements yet</div>', unsafe_allow_html=True)

    elif menu == "Request Leave":
        st.markdown("### Request Leave")
        with st.form("leave_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            start = c1.date_input("Start Date")
            end = c2.date_input("End Date")
            reason = st.text_area("Reason")
            if st.form_submit_button("Submit Request", type="primary", use_container_width=True):
                if start > end:
                    st.error("Invalid date range")
                else:
                    rec = {"employee_id": user["id"], "employee_name": user["name"], "start_date": str(start), "end_date": str(end), "reason": reason, "status": "Pending", "requested_on": datetime.now().strftime("%Y-%m-%d %H:%M")}
                    if add_record(LEAVES_FILE, rec):
                        st.success("Leave request submitted")

    elif menu == "Upload Document":
        st.markdown("### Upload Document")
        with st.form("doc_form", clear_on_submit=True):
            desc = st.text_input("Description")
            file = st.file_uploader("File", type=["pdf","docx","txt","jpg","png","jpeg"])
            if st.form_submit_button("Upload", type="primary", use_container_width=True) and file:
                path = os.path.join(DOCS_DIR, f"{user['id']}_{file.name}")
                with open(path, "wb") as f:
                    f.write(file.getbuffer())
                rec = {"employee_id": user["id"], "employee_name": user["name"], "filename": file.name, "filepath": path, "description": desc, "uploaded_on": datetime.now().strftime("%Y-%m-%d %H:%M")}
                if add_record(DOCUMENTS_FILE, rec):
                    st.success("Document uploaded")

    elif menu == "My Leaves":
        st.markdown("### My Leave Requests")
        leaves = search_records(LEAVES_FILE, "employee_id", user["id"])
        search = st.text_input("Search leaves", placeholder="Filter by reason or date...")
        if search:
            leaves = [l for l in leaves if search.lower() in l["reason"].lower() or search in l["start_date"]]
        if leaves:
            for l in reversed(leaves):
                badge = status_badge(l["status"])
                st.markdown(f'<div class="card">{badge} &nbsp; <strong>{l["start_date"]} → {l["end_date"]}</strong><br>{l["reason"]}<br><small style="color:#6b7280;">Requested {l["requested_on"]}</small></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="empty-state">No leave requests found</div>', unsafe_allow_html=True)

    elif menu == "Announcements":
        st.markdown("### Announcements")
        anns = load_data(ANNOUNCEMENTS_FILE)
        if anns:
            for a in reversed(anns):
                st.markdown(f'<div class="card"><h4>{a["title"]}</h4>{a["content"]}<br><small>By {a["author"]} • {a["date"]}</small></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="empty-state">No announcements</div>', unsafe_allow_html=True)

    elif menu == "Calendar":
        st.markdown("### Leave Calendar")
        leaves = [l for l in load_data(LEAVES_FILE) if l.get("status") == "Approved"]
        if leaves:
            for l in leaves:
                st.markdown(f'<div class="card"><strong>{l["employee_name"]}</strong><br>{l["start_date"]} → {l["end_date"]}<br><small>{l["reason"]}</small></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="empty-state">No approved leaves to show</div>', unsafe_allow_html=True)

else:
    if menu == "Dashboard":
        st.markdown("### HR Dashboard")
        leaves = load_data(LEAVES_FILE)
        pending = [l for l in leaves if l.get("status")=="Pending"]
        c1, c2, c3 = st.columns(3)
        c1.metric("Pending Leaves", len(pending))
        c2.metric("Documents", len(load_data(DOCUMENTS_FILE)))
        c3.metric("Announcements", len(load_data(ANNOUNCEMENTS_FILE)))
        if pending:
            st.info(f"{len(pending)} leave request(s) awaiting approval")

    elif menu == "Manage Leaves":
        st.markdown("### Manage Leaves")
        leaves = load_data(LEAVES_FILE)
        pending = [l for l in leaves if l.get("status")=="Pending"]
        search = st.text_input("Search", placeholder="Employee name or reason...")
        if search:
            pending = [l for l in pending if search.lower() in l["employee_name"].lower() or search.lower() in l["reason"].lower()]
        if not pending:
            st.success("No pending requests")
        else:
            for l in pending:
                badge = status_badge(l["status"])
                st.markdown(f'<div class="card"><strong>{l["employee_name"]}</strong> {badge}<br>{l["start_date"]} → {l["end_date"]}<br>{l["reason"]}<br><small>Requested {l["requested_on"]}</small></div>', unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                if c1.button("Approve", key=f"a{l['id']}", type="primary"):
                    for x in leaves:
                        if x["id"] == l["id"]:
                            x["status"] = "Approved"
                    save_data(LEAVES_FILE, leaves)
                    st.rerun()
                if c2.button("Reject", key=f"r{l['id']}"):
                    for x in leaves:
                        if x["id"] == l["id"]:
                            x["status"] = "Rejected"
                    save_data(LEAVES_FILE, leaves)
                    st.rerun()

    elif menu == "Post Announcement":
        st.markdown("### New Announcement")
        with st.form("ann"):
            title = st.text_input("Title")
            content = st.text_area("Content", height=140)
            if st.form_submit_button("Publish", type="primary", use_container_width=True) and title and content:
                add_record(ANNOUNCEMENTS_FILE, {"title": title, "content": content, "author": user["name"], "date": datetime.now().strftime("%Y-%m-%d %H:%M")})
                st.success("Published")

    elif menu == "View Documents":
        st.markdown("### Documents")
        docs = load_data(DOCUMENTS_FILE)
        search = st.text_input("Search documents", placeholder="Employee or filename...")
        if search:
            docs = [d for d in docs if search.lower() in d["employee_name"].lower() or search.lower() in d["filename"].lower()]
        if docs:
            for d in reversed(docs):
                st.markdown(f'<div class="card"><strong>{d["employee_name"]}</strong> — {d["filename"]}<br>{d.get("description","")}<br><small>{d["uploaded_on"]}</small></div>', unsafe_allow_html=True)
                if os.path.exists(d.get("filepath","")):
                    if d["filename"].lower().endswith((".png",".jpg",".jpeg")):
                        st.image(d["filepath"], width=300)
                    with open(d["filepath"], "rb") as f:
                        st.download_button("Download", f, file_name=d["filename"], key=f"dl{d['id']}")
        else:
            st.markdown('<div class="empty-state">No documents</div>', unsafe_allow_html=True)

    elif menu == "Generate Report":
        st.markdown("### Reports")
        rtype = st.selectbox("Report", ["Pending Leaves", "All Documents", "All Announcements"])
        if st.button("Generate", type="primary"):
            key = {"Pending Leaves":"pending_leaves","All Documents":"all_documents","All Announcements":"announcements"}[rtype]
            data = generate_report(key)
            st.metric("Records", len(data))
            if data:
                st.json(data)

    elif menu == "Add Employee":
        st.markdown("### Add Employee")
        with st.form("add"):
            c1, c2 = st.columns(2)
            name = c1.text_input("Full Name")
            username = c1.text_input("Username")
            password = c1.text_input("Password", type="password")
            dept = c2.text_input("Department")
            email = c2.text_input("Email")
            role = c2.selectbox("Role", ["Employee","HR"])
            if st.form_submit_button("Add", type="primary", use_container_width=True) and name and username:
                add_record(EMPLOYEES_FILE, {"username": username, "password": password, "name": name, "role": role, "department": dept, "email": email})
                st.success(f"{name} added")

    elif menu == "Calendar":
        st.markdown("### Team Leave Calendar")
        approved = [l for l in load_data(LEAVES_FILE) if l.get("status")=="Approved"]
        if approved:
            for l in approved:
                st.markdown(f'<div class="card"><strong>{l["employee_name"]}</strong><br>{l["start_date"]} → {l["end_date"]}<br><small>{l["reason"]}</small></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="empty-state">No approved leaves</div>', unsafe_allow_html=True)
