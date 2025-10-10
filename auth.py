import streamlit as st
import bcrypt
import json
import os
from datetime import datetime, timedelta
import uuid
import time
import random
import string
import re
import pandas as pd

# Constants
ADMIN_FILE = "admin_credentials.json"
ADMIN_LOGS_FILE = "admin_activity.json"
EMAIL_ACCOUNTS_FILE = "email_accounts.json"
USER_ACCOUNTS_FILE = "user_accounts.json"

def generate_secure_password(length=12):
    """Generate a secure password with mixed characters"""
    # Define character sets
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits
    special_chars = "!@#$%^&*"

    # Ensure at least one character from each set
    password = [
        random.choice(lowercase),
        random.choice(uppercase),
        random.choice(digits),
        random.choice(special_chars)
    ]

    # Fill the rest with random characters from all sets
    all_chars = lowercase + uppercase + digits + special_chars
    for _ in range(length - 4):
        password.append(random.choice(all_chars))

    # Shuffle the password list
    random.shuffle(password)

    return ''.join(password)

def check_password_strength(password):
    """Check password strength and return score with display"""
    score = 0
    feedback = []

    # Length check
    if len(password) >= 8:
        score += 1
    else:
        feedback.append("At least 8 characters")

    # Uppercase check
    if re.search(r'[A-Z]', password):
        score += 1
    else:
        feedback.append("Uppercase letter")

    # Lowercase check
    if re.search(r'[a-z]', password):
        score += 1
    else:
        feedback.append("Lowercase letter")

    # Digit check
    if re.search(r'\d', password):
        score += 1
    else:
        feedback.append("Number")

    # Special character check
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        score += 1

    # Determine strength
    if score >= 4:
        strength = "🟢 Strong"
    elif score >= 3:
        strength = "🟡 Medium"
    elif score >= 2:
        strength = "🟠 Weak"
    else:
        strength = "🔴 Very Weak"

    return {
        'score': score,
        'display': strength,
        'feedback': feedback
    }

def load_email_accounts():
    """Load email accounts from JSON file"""
    if os.path.exists(EMAIL_ACCOUNTS_FILE):
        try:
            with open(EMAIL_ACCOUNTS_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading email accounts: {e}")
            return {}
    return {}

def save_email_accounts(accounts):
    """Save email accounts to JSON file"""
    try:
        with open(EMAIL_ACCOUNTS_FILE, 'w') as f:
            json.dump(accounts, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving email accounts: {e}")
        return False

def encrypt_password(password):
    """Simple encryption for email passwords (base64 encoding)"""
    import base64
    return base64.b64encode(password.encode()).decode()

def decrypt_password(encrypted_password):
    """Simple decryption for email passwords (base64 decoding)"""
    import base64
    try:
        return base64.b64decode(encrypted_password.encode()).decode()
    except:
        return encrypted_password  # Return as-is if decryption fails

def add_email_account(email, password, display_name, is_default=False, added_by=""):
    """Add a new email account"""
    accounts = load_email_accounts()

    if email in accounts:
        return {"success": False, "message": "Email account already exists"}

    # If this is the first account or is_default is True, make it default
    if not accounts or is_default:
        # Remove default from other accounts
        for acc in accounts.values():
            acc['is_default'] = False

    accounts[email] = {
        "id": str(uuid.uuid4()),
        "email": email,
        "password": encrypt_password(password),
        "display_name": display_name,
        "is_default": is_default or len(accounts) == 0,
        "status": "active",
        "added_by": added_by,
        "added_at": datetime.now().isoformat(),
        "last_used": None,
        "total_sent": 0
    }

    if save_email_accounts(accounts):
        log_admin_activity(added_by, "email_account_added", {"email": email, "display_name": display_name})
        return {"success": True, "message": f"Email account {email} added successfully"}
    else:
        return {"success": False, "message": "Failed to save email account"}

def update_email_account(email, updates, updated_by=""):
    """Update an email account"""
    accounts = load_email_accounts()

    if email not in accounts:
        return {"success": False, "message": "Email account not found"}

    # Update fields
    for key, value in updates.items():
        if key == "password" and value:
            accounts[email]["password"] = encrypt_password(value)
        elif key in ["display_name", "status", "is_default"]:
            accounts[email][key] = value

    # If setting as default, remove default from others
    if updates.get("is_default"):
        for acc_email, acc_data in accounts.items():
            if acc_email != email:
                acc_data["is_default"] = False

    accounts[email]["updated_at"] = datetime.now().isoformat()
    accounts[email]["updated_by"] = updated_by

    if save_email_accounts(accounts):
        log_admin_activity(updated_by, "email_account_updated", {"email": email, "updates": list(updates.keys())})
        return {"success": True, "message": f"Email account {email} updated successfully"}
    else:
        return {"success": False, "message": "Failed to update email account"}

def delete_email_account(email, deleted_by=""):
    """Delete an email account"""
    accounts = load_email_accounts()

    if email not in accounts:
        return {"success": False, "message": "Email account not found"}

    # Don't allow deleting the last account
    if len(accounts) == 1:
        return {"success": False, "message": "Cannot delete the last email account"}

    was_default = accounts[email].get("is_default", False)
    del accounts[email]

    # If deleted account was default, make another one default
    if was_default and accounts:
        first_email = list(accounts.keys())[0]
        accounts[first_email]["is_default"] = True

    if save_email_accounts(accounts):
        log_admin_activity(deleted_by, "email_account_deleted", {"email": email})
        return {"success": True, "message": f"Email account {email} deleted successfully"}
    else:
        return {"success": False, "message": "Failed to delete email account"}

def test_email_account(email, password):
    """Test email account connectivity"""
    import smtplib
    from email.mime.text import MIMEText

    try:
        # Gmail SMTP configuration
        smtp_server = "smtp.gmail.com"
        smtp_port = 587

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(email, password)
        server.quit()

        return {"success": True, "message": "Email account connection successful"}
    except Exception as e:
        return {"success": False, "message": f"Connection failed: {str(e)}"}

def get_default_email_account():
    """Get the default email account for sending"""
    accounts = load_email_accounts()

    for email, data in accounts.items():
        if data.get("is_default") and data.get("status") == "active":
            return {
                "email": email,
                "password": decrypt_password(data["password"]),
                "display_name": data.get("display_name", email)
            }

    # If no default found, return the first active account
    for email, data in accounts.items():
        if data.get("status") == "active":
            return {
                "email": email,
                "password": decrypt_password(data["password"]),
                "display_name": data.get("display_name", email)
            }

    return None

# User Account Management Functions
def load_user_accounts():
    """Load user accounts from JSON file"""
    if os.path.exists(USER_ACCOUNTS_FILE):
        try:
            with open(USER_ACCOUNTS_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading user accounts: {e}")
            return {}
    return {}

def save_user_accounts(accounts):
    """Save user accounts to JSON file"""
    try:
        with open(USER_ACCOUNTS_FILE, 'w') as f:
            json.dump(accounts, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving user accounts: {e}")
        return False

def validate_password_strength(password):
    """Validate password strength for user registration"""
    if len(password) < 8:
        return {"valid": False, "message": "Password must be at least 8 characters long"}

    if not re.search(r'[A-Z]', password):
        return {"valid": False, "message": "Password must contain at least one uppercase letter"}

    if not re.search(r'[a-z]', password):
        return {"valid": False, "message": "Password must contain at least one lowercase letter"}

    if not re.search(r'\d', password):
        return {"valid": False, "message": "Password must contain at least one number"}

    return {"valid": True, "message": "Password meets all requirements"}

def validate_email_format(email):
    """Validate email format"""
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(email_pattern, email):
        return {"valid": True, "message": "Valid email format"}
    else:
        return {"valid": False, "message": "Invalid email format"}

def create_user_account(email, password, confirm_password):
    """Create a new user account"""
    # Validate inputs
    if not email or not password or not confirm_password:
        return {"success": False, "message": "All fields are required"}

    # Validate email format
    email_validation = validate_email_format(email)
    if not email_validation["valid"]:
        return {"success": False, "message": email_validation["message"]}

    # Check password match
    if password != confirm_password:
        return {"success": False, "message": "Passwords do not match"}

    # Validate password strength
    password_validation = validate_password_strength(password)
    if not password_validation["valid"]:
        return {"success": False, "message": password_validation["message"]}

    # Load existing accounts
    user_accounts = load_user_accounts()
    admin_accounts = load_admin_credentials()

    # Check if email already exists in user accounts
    if email in user_accounts:
        return {"success": False, "message": "Email address already registered"}

    # Check if email already exists in admin accounts
    if email in admin_accounts:
        return {"success": False, "message": "Email address already registered as admin"}

    # Create new user account
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    user_accounts[email] = {
        "id": str(uuid.uuid4()),
        "email": email,
        "password": hashed_password,
        "status": "active",
        "role": "user",
        "created_at": datetime.now().isoformat(),
        "last_login": None,
        "login_attempts": 0,
        "locked_until": None
    }

    # Save accounts
    if save_user_accounts(user_accounts):
        # Log the registration
        log_admin_activity("system", "user_registered", {"email": email})
        return {"success": True, "message": "Account created successfully! You can now log in."}
    else:
        return {"success": False, "message": "Failed to save account. Please try again."}

def authenticate_user(email, password):
    """Authenticate user credentials"""
    user_accounts = load_user_accounts()

    if email not in user_accounts:
        return {"success": False, "message": "Invalid email or password", "user": None}

    user = user_accounts[email]

    # Check if account is locked
    if user.get("locked_until"):
        locked_until = datetime.fromisoformat(user["locked_until"])
        if datetime.now() < locked_until:
            remaining = locked_until - datetime.now()
            minutes = int(remaining.total_seconds() / 60)
            return {"success": False, "message": f"Account locked for {minutes} more minutes", "user": None}
        else:
            # Unlock account
            user["locked_until"] = None
            user["login_attempts"] = 0

    # Check if account is active
    if user.get("status") != "active":
        return {"success": False, "message": "Account is deactivated. Contact administrator.", "user": None}

    # Verify password
    if bcrypt.checkpw(password.encode('utf-8'), user["password"].encode('utf-8')):
        # Successful login
        user["last_login"] = datetime.now().isoformat()
        user["login_attempts"] = 0
        user["locked_until"] = None
        save_user_accounts(user_accounts)

        log_admin_activity(email, "user_login_success", {"timestamp": datetime.now().isoformat()})
        return {"success": True, "message": "Login successful", "user": user}
    else:
        # Failed login
        user["login_attempts"] = user.get("login_attempts", 0) + 1

        if user["login_attempts"] >= 5:
            # Lock account for 30 minutes
            user["locked_until"] = (datetime.now() + timedelta(minutes=30)).isoformat()
            save_user_accounts(user_accounts)
            log_admin_activity(email, "user_account_locked", {"attempts": user["login_attempts"]})
            return {"success": False, "message": "Account locked due to too many failed attempts. Try again in 30 minutes.", "user": None}

        save_user_accounts(user_accounts)
        remaining_attempts = 5 - user["login_attempts"]
        log_admin_activity(email, "user_login_failed", {"attempts": user["login_attempts"]})
        return {"success": False, "message": f"Invalid email or password. {remaining_attempts} attempts remaining.", "user": None}

def login_user(email, user_info):
    """Set user as logged in"""
    st.session_state.user_logged_in = True
    st.session_state.user_email = email
    st.session_state.user_info = user_info
    st.session_state.login_time = datetime.now()
    st.session_state.session_id = str(uuid.uuid4())

def logout_user():
    """Log out current user"""
    if st.session_state.get('user_logged_in'):
        log_admin_activity(st.session_state.get('user_email', 'unknown'), "user_logout", {})

    # Clear user session states
    user_keys = ['user_logged_in', 'user_email', 'user_info', 'login_time', 'session_id']
    for key in user_keys:
        if key in st.session_state:
            del st.session_state[key]

def is_user_logged_in():
    """Check if a user is currently logged in"""
    return st.session_state.get('user_logged_in', False)

def get_current_user():
    """Get current logged in user email"""
    return st.session_state.get('user_email', '')

def get_current_user_info():
    """Get current user information"""
    user_accounts = load_user_accounts()
    email = get_current_user()
    return user_accounts.get(email, {})

def update_user_status(email, status, updated_by=""):
    """Update user account status (admin function)"""
    user_accounts = load_user_accounts()

    if email not in user_accounts:
        return {"success": False, "message": "User account not found"}

    user_accounts[email]["status"] = status
    user_accounts[email]["updated_at"] = datetime.now().isoformat()
    user_accounts[email]["updated_by"] = updated_by

    if save_user_accounts(user_accounts):
        log_admin_activity(updated_by, "user_status_updated", {"email": email, "status": status})
        return {"success": True, "message": f"User account {status} successfully"}
    else:
        return {"success": False, "message": "Failed to update user status"}

def delete_user_account(email, deleted_by=""):
    """Delete user account (admin function)"""
    user_accounts = load_user_accounts()

    if email not in user_accounts:
        return {"success": False, "message": "User account not found"}

    del user_accounts[email]

    if save_user_accounts(user_accounts):
        log_admin_activity(deleted_by, "user_account_deleted", {"email": email})
        return {"success": True, "message": "User account deleted successfully"}
    else:
        return {"success": False, "message": "Failed to delete user account"}

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def load_admin_credentials():
    """Load admin credentials from file"""
    if os.path.exists(ADMIN_FILE):
        with open(ADMIN_FILE, 'r') as f:
            return json.load(f)
    else:
        # Create default primary admin if file doesn't exist
        admin_id = str(uuid.uuid4())
        default_admin = {
            "admin@reminder.com": {
                "id": admin_id,
                "password_hash": hash_password("Admin@123"),
                "role": "primary_admin",
                "status": "active",
                "created_at": datetime.now().isoformat(),
                "created_by": "system",
                "last_login": None,
                "login_attempts": 0,
                "locked_until": None,
                "permissions": {
                    "manage_users": True,
                    "lock_unlock_users": True,
                    "view_logs": True,
                    "system_admin": True
                }
            }
        }
        save_admin_credentials(default_admin)
        log_admin_activity("system", "admin_created", {"email": "admin@reminder.com", "role": "primary_admin"})
        return default_admin

def save_admin_credentials(credentials):
    """Save admin credentials to file"""
    with open(ADMIN_FILE, 'w') as f:
        json.dump(credentials, f, indent=2)

def log_admin_activity(admin_email: str, action: str, details: dict = None):
    """Log admin activity"""
    try:
        if os.path.exists(ADMIN_LOGS_FILE):
            with open(ADMIN_LOGS_FILE, 'r') as f:
                logs = json.load(f)
        else:
            logs = []

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "admin_email": admin_email,
            "action": action,
            "details": details or {},
            "ip_address": "localhost",  # In production, get real IP
            "session_id": st.session_state.get('session_id', 'unknown')
        }

        logs.append(log_entry)

        # Keep only last 1000 entries
        if len(logs) > 1000:
            logs = logs[-1000:]

        with open(ADMIN_LOGS_FILE, 'w') as f:
            json.dump(logs, f, indent=2)
    except Exception as e:
        st.error(f"Error logging activity: {e}")

def authenticate_admin(email: str, password: str) -> dict:
    """Authenticate admin credentials - returns dict with status and user info"""
    credentials = load_admin_credentials()

    if email not in credentials:
        log_admin_activity(email, "login_failed", {"reason": "email_not_found"})
        return {"success": False, "message": "Invalid email or password", "user": None}

    user = credentials[email]

    # Check if account is locked
    if user.get("status") == "locked":
        locked_until = user.get("locked_until")
        if locked_until:
            lock_time = datetime.fromisoformat(locked_until)
            if datetime.now() < lock_time:
                log_admin_activity(email, "login_failed", {"reason": "account_locked"})
                return {"success": False, "message": "Account is locked. Contact administrator.", "user": None}
            else:
                # Auto-unlock if lock period expired
                user["status"] = "active"
                user["locked_until"] = None
                user["login_attempts"] = 0
        else:
            log_admin_activity(email, "login_failed", {"reason": "account_locked_permanent"})
            return {"success": False, "message": "Account is permanently locked. Contact administrator.", "user": None}

    # Check password
    stored_hash = user["password_hash"]
    if verify_password(password, stored_hash):
        # Successful login
        user["last_login"] = datetime.now().isoformat()
        user["login_attempts"] = 0
        save_admin_credentials(credentials)
        log_admin_activity(email, "login_success", {"role": user.get("role", "admin")})
        return {"success": True, "message": "Login successful", "user": user}
    else:
        # Failed login - increment attempts
        user["login_attempts"] = user.get("login_attempts", 0) + 1

        # Lock account after 5 failed attempts
        if user["login_attempts"] >= 5:
            user["status"] = "locked"
            user["locked_until"] = (datetime.now() + timedelta(hours=1)).isoformat()
            log_admin_activity(email, "account_auto_locked", {"attempts": user["login_attempts"]})
            save_admin_credentials(credentials)
            return {"success": False, "message": "Account locked due to multiple failed attempts. Try again in 1 hour.", "user": None}

        save_admin_credentials(credentials)
        log_admin_activity(email, "login_failed", {"reason": "wrong_password", "attempts": user["login_attempts"]})
        return {"success": False, "message": f"Invalid email or password. {5 - user['login_attempts']} attempts remaining.", "user": None}

def add_new_admin(email: str, password: str, role: str, current_admin_email: str) -> dict:
    """Add a new admin (only existing admins can do this)"""
    if not is_admin_logged_in():
        return {"success": False, "message": "Not logged in"}

    current_user = get_current_user_info()
    if not current_user.get("permissions", {}).get("manage_users", False):
        return {"success": False, "message": "Insufficient permissions"}

    credentials = load_admin_credentials()

    if email in credentials:
        return {"success": False, "message": "Admin already exists"}

    # Validate role
    valid_roles = ["admin", "primary_admin"] if current_user.get("role") == "primary_admin" else ["admin"]
    if role not in valid_roles:
        return {"success": False, "message": "Invalid role"}

    admin_id = str(uuid.uuid4())
    permissions = {
        "manage_users": role == "primary_admin",
        "lock_unlock_users": role == "primary_admin",
        "view_logs": True,
        "system_admin": role == "primary_admin"
    }

    credentials[email] = {
        "id": admin_id,
        "password_hash": hash_password(password),
        "role": role,
        "status": "active",
        "created_at": datetime.now().isoformat(),
        "created_by": current_admin_email,
        "last_login": None,
        "login_attempts": 0,
        "locked_until": None,
        "permissions": permissions
    }

    save_admin_credentials(credentials)
    log_admin_activity(current_admin_email, "admin_created", {"new_admin": email, "role": role})
    return {"success": True, "message": "Admin created successfully"}

def lock_unlock_user(target_email: str, action: str, current_admin_email: str, duration_hours: int = None) -> dict:
    """Lock or unlock a user account"""
    if not is_admin_logged_in():
        return {"success": False, "message": "Not logged in"}

    current_user = get_current_user_info()
    if not current_user.get("permissions", {}).get("lock_unlock_users", False):
        return {"success": False, "message": "Insufficient permissions to lock/unlock users"}

    credentials = load_admin_credentials()

    if target_email not in credentials:
        return {"success": False, "message": "User not found"}

    if target_email == current_admin_email:
        return {"success": False, "message": "Cannot lock/unlock yourself"}

    target_user = credentials[target_email]

    # Prevent locking primary admin by regular admin
    if target_user.get("role") == "primary_admin" and current_user.get("role") != "primary_admin":
        return {"success": False, "message": "Cannot lock/unlock primary admin"}

    if action == "lock":
        target_user["status"] = "locked"
        if duration_hours:
            target_user["locked_until"] = (datetime.now() + timedelta(hours=duration_hours)).isoformat()
        else:
            target_user["locked_until"] = None  # Permanent lock

        log_admin_activity(current_admin_email, "user_locked", {
            "target_user": target_email,
            "duration_hours": duration_hours
        })
        message = f"User {target_email} locked successfully"

    elif action == "unlock":
        target_user["status"] = "active"
        target_user["locked_until"] = None
        target_user["login_attempts"] = 0

        log_admin_activity(current_admin_email, "user_unlocked", {"target_user": target_email})
        message = f"User {target_email} unlocked successfully"

    else:
        return {"success": False, "message": "Invalid action"}

    save_admin_credentials(credentials)
    return {"success": True, "message": message}

def delete_admin(target_email: str, current_admin_email: str) -> dict:
    """Delete an admin account"""
    if not is_admin_logged_in():
        return {"success": False, "message": "Not logged in"}

    current_user = get_current_user_info()
    if not current_user.get("permissions", {}).get("manage_users", False):
        return {"success": False, "message": "Insufficient permissions"}

    credentials = load_admin_credentials()

    if target_email not in credentials:
        return {"success": False, "message": "User not found"}

    if target_email == current_admin_email:
        return {"success": False, "message": "Cannot delete yourself"}

    target_user = credentials[target_email]

    # Prevent deleting primary admin by regular admin
    if target_user.get("role") == "primary_admin" and current_user.get("role") != "primary_admin":
        return {"success": False, "message": "Cannot delete primary admin"}

    # Prevent deleting the last primary admin
    primary_admins = [email for email, user in credentials.items() if user.get("role") == "primary_admin"]
    if target_user.get("role") == "primary_admin" and len(primary_admins) <= 1:
        return {"success": False, "message": "Cannot delete the last primary admin"}

    del credentials[target_email]
    save_admin_credentials(credentials)
    log_admin_activity(current_admin_email, "admin_deleted", {"deleted_admin": target_email})

    return {"success": True, "message": f"Admin {target_email} deleted successfully"}

def change_admin_email(old_email: str, new_email: str, current_admin_email: str) -> dict:
    """Change an admin's email address"""
    if not is_admin_logged_in():
        return {"success": False, "message": "Not logged in"}

    current_user = get_current_user_info()
    if not current_user.get("permissions", {}).get("manage_users", False):
        return {"success": False, "message": "Insufficient permissions"}

    credentials = load_admin_credentials()

    if old_email not in credentials:
        return {"success": False, "message": "User not found"}

    if new_email in credentials:
        return {"success": False, "message": "New email already exists"}

    # Validate email format
    import re
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, new_email):
        return {"success": False, "message": "Invalid email format"}

    target_user = credentials[old_email]

    # Only allow changing own email or if you're primary admin
    if old_email != current_admin_email and current_user.get("role") != "primary_admin":
        return {"success": False, "message": "Can only change your own email or you need primary admin privileges"}

    # Move user data to new email key
    credentials[new_email] = target_user
    del credentials[old_email]

    save_admin_credentials(credentials)
    log_admin_activity(current_admin_email, "email_changed", {
        "old_email": old_email,
        "new_email": new_email
    })

    # If changing own email, update session
    if old_email == current_admin_email:
        st.session_state.admin_email = new_email

    return {"success": True, "message": f"Email changed from {old_email} to {new_email}"}

def change_admin_password(target_email: str, new_password: str, current_admin_email: str) -> dict:
    """Change an admin's password"""
    if not is_admin_logged_in():
        return {"success": False, "message": "Not logged in"}

    current_user = get_current_user_info()
    credentials = load_admin_credentials()

    if target_email not in credentials:
        return {"success": False, "message": "User not found"}

    # Only allow changing own password or if you're primary admin
    if target_email != current_admin_email and current_user.get("role") != "primary_admin":
        return {"success": False, "message": "Can only change your own password or you need primary admin privileges"}

    # Validate password strength
    if len(new_password) < 8:
        return {"success": False, "message": "Password must be at least 8 characters long"}

    # Update password
    credentials[target_email]["password_hash"] = hash_password(new_password)
    credentials[target_email]["login_attempts"] = 0  # Reset failed attempts

    save_admin_credentials(credentials)
    log_admin_activity(current_admin_email, "password_changed", {"target_email": target_email})

    return {"success": True, "message": "Password changed successfully"}

def is_admin_logged_in() -> bool:
    """Check if admin is logged in"""
    return st.session_state.get('admin_logged_in', False)

def get_current_admin() -> str:
    """Get current admin email"""
    return st.session_state.get('admin_email', '')

def get_current_user_info() -> dict:
    """Get current user information"""
    if not is_admin_logged_in():
        return {}

    credentials = load_admin_credentials()
    email = get_current_admin()
    return credentials.get(email, {})

def login_admin(email: str, user_info: dict):
    """Set admin as logged in"""
    st.session_state.admin_logged_in = True
    st.session_state.admin_email = email
    st.session_state.admin_user_info = user_info
    st.session_state.login_time = datetime.now()
    st.session_state.session_id = str(uuid.uuid4())

def logout_admin():
    """Logout admin"""
    if is_admin_logged_in():
        log_admin_activity(get_current_admin(), "logout", {})

    st.session_state.admin_logged_in = False
    st.session_state.admin_email = ''
    st.session_state.admin_user_info = {}
    st.session_state.login_time = None
    st.session_state.session_id = None

    # Clear other session states
    for key in list(st.session_state.keys()):
        if key not in ['admin_logged_in', 'admin_email', 'admin_user_info', 'login_time', 'session_id']:
            del st.session_state[key]

def show_login_page():
    """Display the enhanced login page with user registration"""
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 2rem 0;">
            <h1>🔐 Welcome to Reminder System</h1>
            <p style="color: #666;">Secure Authentication & User Management</p>
        </div>
        """, unsafe_allow_html=True)

        # Login/Registration tabs
        login_tab, register_tab = st.tabs(["🔑 Login", "👤 Create Account"])

        with login_tab:
            # Show system status
            credentials = load_admin_credentials()
            user_accounts = load_user_accounts()
            total_admins = len(credentials)
            total_users = len(user_accounts)
            active_admins = len([u for u in credentials.values() if u.get("status") == "active"])
            active_users = len([u for u in user_accounts.values() if u.get("status") == "active"])

            col_info1, col_info2, col_info3, col_info4 = st.columns(4)
            with col_info1:
                st.metric("👑 Admins", total_admins)
            with col_info2:
                st.metric("👥 Users", total_users)
            with col_info3:
                st.metric("✅ Active Admins", active_admins)
            with col_info4:
                st.metric("✅ Active Users", active_users)

            st.divider()

            # Login type selection
            login_type = st.radio(
                "Select Login Type:",
                ["🔑 Admin Login", "👤 User Login"],
                horizontal=True,
                help="Choose whether you're logging in as an admin or regular user"
            )

            with st.form("login_form"):
                if login_type == "🔑 Admin Login":
                    st.markdown("### 🔑 Admin Login")
                    email_placeholder = "admin@reminder.com"
                    email_help = "Enter your registered admin email"
                else:
                    st.markdown("### 👤 User Login")
                    email_placeholder = "user@example.com"
                    email_help = "Enter your registered user email"

                email = st.text_input(
                    "📧 Email Address",
                    placeholder=email_placeholder,
                    help=email_help
                )

                password = st.text_input(
                    "🔒 Password",
                    type="password",
                    placeholder="Enter your password",
                    help="Enter your password"
                )

                col_a, col_b, col_c = st.columns([1, 2, 1])
                with col_b:
                    login_submitted = st.form_submit_button(
                        f"🚀 Login as {login_type.split()[1]}",
                        type="primary",
                        use_container_width=True
                    )

                if login_submitted:
                    if email and password:
                        if login_type == "🔑 Admin Login":
                            auth_result = authenticate_admin(email, password)
                            if auth_result["success"]:
                                login_admin(email, auth_result["user"])
                                st.success("✅ Admin login successful! Redirecting to dashboard...")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error(f"❌ {auth_result['message']}")
                                if "locked" in auth_result["message"].lower():
                                    st.warning("🔒 If you believe this is an error, contact the primary administrator.")
                        else:
                            # User login
                            auth_result = authenticate_user(email, password)
                            if auth_result["success"]:
                                login_user(email, auth_result["user"])
                                st.success("✅ User login successful! Redirecting to dashboard...")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error(f"❌ {auth_result['message']}")
                    else:
                        st.warning("⚠️ Please enter both email and password.")

            # Quick access for default admin
            if login_type == "🔑 Admin Login":
                st.markdown("---")
                st.markdown("**Default Admin Access:**")
                col_quick1, col_quick2 = st.columns(2)
                with col_quick1:
                    if st.button("🚀 Quick Admin Login", help="Login with default admin credentials"):
                        auth_result = authenticate_admin("admin@reminder.com", "Admin@123")
                        if auth_result["success"]:
                            login_admin("admin@reminder.com", auth_result["user"])
                            st.success("✅ Quick admin login successful!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ Default admin login failed")

        with register_tab:
            st.markdown("### 👤 Create New Account")
            st.info("📝 Register for a new user account to access the Reminder System")

            with st.form("register_form"):
                reg_email = st.text_input(
                    "📧 Email Address*",
                    placeholder="your.email@example.com",
                    help="Enter a valid email address (must be unique)"
                )

                col_pass1, col_pass2 = st.columns(2)
                with col_pass1:
                    reg_password = st.text_input(
                        "🔒 Password*",
                        type="password",
                        placeholder="Enter password",
                        help="Minimum 8 characters with uppercase, lowercase, and number"
                    )

                with col_pass2:
                    reg_confirm_password = st.text_input(
                        "🔒 Confirm Password*",
                        type="password",
                        placeholder="Confirm password",
                        help="Re-enter your password"
                    )

                # Password requirements
                st.markdown("""
                **Password Requirements:**
                - ✅ At least 8 characters long
                - ✅ Contains uppercase letter (A-Z)
                - ✅ Contains lowercase letter (a-z)
                - ✅ Contains at least one number (0-9)
                """)

                col_reg_a, col_reg_b, col_reg_c = st.columns([1, 2, 1])
                with col_reg_b:
                    register_submitted = st.form_submit_button(
                        "🎉 Create Account",
                        type="primary",
                        use_container_width=True
                    )

                if register_submitted:
                    if reg_email and reg_password and reg_confirm_password:
                        result = create_user_account(reg_email, reg_password, reg_confirm_password)
                        if result["success"]:
                            st.success(f"✅ {result['message']}")
                            st.balloons()
                            st.info("🔄 Please switch to the Login tab to access your account.")
                            time.sleep(3)
                            st.rerun()
                        else:
                            st.error(f"❌ {result['message']}")
                    else:
                        st.warning("⚠️ Please fill in all required fields.")

        # Security information
        with st.expander("🔒 Security Information"):
            st.markdown("""
            **Security Features:**
            - 🔐 bcrypt password hashing for all accounts
            - 🚫 Account lockout after 5 failed attempts (30 min)
            - 📝 Complete activity logging and audit trails
            - 👑 Role-based access control (Admin/User)
            - 🛡️ Session management with automatic timeout
            - 🔄 Secure password validation and requirements

            **Account Types:**
            - **👑 Admin:** Full system access, user management, email configuration
            - **👤 User:** Access to reminder system, personal data management

            **Default Admin Credentials:**
            - Email: admin@reminder.com
            - Password: Admin@123

            **Need Help?**
            - For account issues: Contact your system administrator
            - For password reset: Contact admin for manual reset
            - For technical support: Check system logs or contact IT
            """)

        # Default credentials info (only show if no custom admins exist)
        if total_admins == 1 and "admin@reminder.com" in credentials:
            with st.expander("ℹ️ Default Admin Credentials"):
                st.code("""
Email: admin@reminder.com
Password: Admin@123
                """)
                st.warning("⚠️ Change these credentials after first login for security!")

        # Emergency contact info
        st.markdown("""
        <div style="text-align: center; margin-top: 2rem; padding: 1rem; background-color: #f0f2f6; border-radius: 0.5rem;">
            <small>🆘 <strong>Account Locked?</strong> Contact your system administrator</small>
        </div>
        """, unsafe_allow_html=True)

def show_admin_header():
    """Show admin header with logout option"""
    user_info = get_current_user_info()
    admin_email = get_current_admin()

    # Create header with user info and logout
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        role = user_info.get('role', 'admin')
        role_icon = "👑" if role == "primary_admin" else "👤"
        login_time = st.session_state.get('login_time')

        if login_time:
            time_str = login_time.strftime("%Y-%m-%d %H:%M")
            st.markdown(f"{role_icon} **Welcome, {admin_email}** ({role}) | 🕐 {time_str}")
        else:
            st.markdown(f"{role_icon} **Welcome, {admin_email}** ({role})")

    with col2:
        # Show permissions indicator
        permissions = user_info.get('permissions', {})
        if permissions.get('system_admin'):
            st.markdown("🔧 **System Admin**")
        elif permissions.get('manage_users'):
            st.markdown("👥 **User Manager**")
        else:
            st.markdown("📧 **Standard Admin**")

    with col3:
        if st.button("🚪 Logout", type="secondary"):
            logout_admin()
            st.rerun()

    # Show quick stats
    if user_info.get('permissions', {}).get('view_logs'):
        credentials = load_admin_credentials()
        total_users = len(credentials)
        active_users = len([u for u in credentials.values() if u.get("status") == "active"])

        col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
        with col_stat1:
            st.metric("👥 Total Users", total_users)
        with col_stat2:
            st.metric("✅ Active", active_users)
        with col_stat3:
            st.metric("🔒 Locked", total_users - active_users)
        with col_stat4:
            session_time = datetime.now() - st.session_state.get('login_time', datetime.now())
            hours = int(session_time.total_seconds() // 3600)
            minutes = int((session_time.total_seconds() % 3600) // 60)
            st.metric("⏱️ Session", f"{hours}h {minutes}m")

    st.divider()

def require_admin_login():
    """Decorator function to require admin login"""
    if not is_admin_logged_in():
        show_login_page()
        st.stop()
    else:
        show_admin_header()

def show_admin_management():
    """Show comprehensive admin management interface"""
    current_user = get_current_user_info()
    current_admin = get_current_admin()

    if not current_user.get('permissions', {}).get('manage_users'):
        st.error("❌ You don't have permission to access admin management.")
        return

    st.title("👥 Advanced Admin Management")
    st.markdown("**Comprehensive user management with role-based access control**")

    # Load data
    credentials = load_admin_credentials()

    # Management tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["👥 Admin Management", "➕ Add New Admin", "✏️ Edit Admin Details", "👤 User Accounts", "📧 Email Management", "📊 Analytics", "📝 Activity Logs"])

    with tab1:
        st.subheader("🔧 User Management & Control")

        # Filters
        col_filter1, col_filter2, col_filter3 = st.columns(3)
        with col_filter1:
            status_filter = st.selectbox("Filter by Status", ["All", "Active", "Locked"])
        with col_filter2:
            role_filter = st.selectbox("Filter by Role", ["All", "primary_admin", "admin"])
        with col_filter3:
            sort_by = st.selectbox("Sort by", ["Email", "Last Login", "Created Date", "Role"])

        st.divider()

        # User management table
        for email, user_data in credentials.items():
            # Apply filters
            if status_filter != "All" and user_data.get("status", "active").title() != status_filter:
                continue
            if role_filter != "All" and user_data.get("role", "admin") != role_filter:
                continue

            # User card
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 2, 2, 3])

                with col1:
                    role = user_data.get('role', 'admin')
                    status = user_data.get('status', 'active')
                    role_icon = "👑" if role == "primary_admin" else "👤"
                    status_icon = "✅" if status == "active" else "🔒"

                    st.markdown(f"**{role_icon} {email}**")
                    st.markdown(f"{status_icon} {status.title()} | {role.replace('_', ' ').title()}")

                with col2:
                    last_login = user_data.get('last_login')
                    if last_login:
                        login_date = datetime.fromisoformat(last_login).strftime("%m/%d %H:%M")
                        st.write(f"🕐 {login_date}")
                    else:
                        st.write("🕐 Never")

                    attempts = user_data.get('login_attempts', 0)
                    if attempts > 0:
                        st.write(f"⚠️ {attempts} failed attempts")

                with col3:
                    created_date = user_data.get('created_at', '')
                    if created_date:
                        created = datetime.fromisoformat(created_date).strftime("%Y-%m-%d")
                        st.write(f"📅 Created: {created}")

                    created_by = user_data.get('created_by', 'Unknown')
                    st.write(f"👤 By: {created_by}")

                with col4:
                    if email == current_admin:
                        st.info("👤 This is you")
                    else:
                        # Action buttons
                        col_btn1, col_btn2, col_btn3 = st.columns(3)

                        # Lock/Unlock button
                        if current_user.get('permissions', {}).get('lock_unlock_users'):
                            with col_btn1:
                                if user_data.get('status') == 'active':
                                    if st.button(f"🔒 Lock", key=f"lock_{email}", help="Lock this user"):
                                        result = lock_unlock_user(email, "lock", current_admin)
                                        if result["success"]:
                                            st.success(result["message"])
                                            st.rerun()
                                        else:
                                            st.error(result["message"])
                                else:
                                    if st.button(f"🔓 Unlock", key=f"unlock_{email}", help="Unlock this user"):
                                        result = lock_unlock_user(email, "unlock", current_admin)
                                        if result["success"]:
                                            st.success(result["message"])
                                            st.rerun()
                                        else:
                                            st.error(result["message"])

                        # Reset attempts button
                        with col_btn2:
                            if user_data.get('login_attempts', 0) > 0:
                                if st.button(f"🔄 Reset", key=f"reset_{email}", help="Reset failed login attempts"):
                                    credentials[email]['login_attempts'] = 0
                                    save_admin_credentials(credentials)
                                    log_admin_activity(current_admin, "attempts_reset", {"target_user": email})
                                    st.success("Login attempts reset!")
                                    st.rerun()

                        # Delete button
                        with col_btn3:
                            if current_user.get('permissions', {}).get('manage_users'):
                                if st.button(f"🗑️ Delete", key=f"delete_{email}", help="Delete this user"):
                                    result = delete_admin(email, current_admin)
                                    if result["success"]:
                                        st.success(result["message"])
                                        st.rerun()
                                    else:
                                        st.error(result["message"])

                st.divider()

    with tab2:
        st.subheader("➕ Add New Administrator")

        # Quick Admin Creation Section
        with st.expander("⚡ Quick Admin Creation (Auto-Generated Password)", expanded=False):
            st.markdown("**Create an admin account instantly with a secure auto-generated password**")

            col_quick1, col_quick2, col_quick3 = st.columns([2, 1, 1])

            with col_quick1:
                quick_email = st.text_input("📧 Email for new admin", placeholder="admin@reminder.com", key="quick_email")

            with col_quick2:
                quick_role = st.selectbox("Role", ["admin", "primary_admin"] if current_user.get('role') == 'primary_admin' else ["admin"], key="quick_role")

            with col_quick3:
                if st.button("🚀 Create Now", type="primary", help="Creates admin with secure auto-generated password"):
                    if quick_email:
                        if quick_email in credentials:
                            st.error("❌ Admin with this email already exists!")
                        else:
                            # Generate secure password
                            auto_password = generate_secure_password()

                            # Create admin
                            result = add_new_admin(quick_email, auto_password, quick_role, current_admin)
                            if result["success"]:
                                st.success(f"✅ Admin created successfully!")

                                # Show credentials immediately
                                st.markdown("### 🎉 **Admin Account Created!**")
                                st.code(f"Email: {quick_email}\nPassword: {auto_password}")
                                st.warning("⚠️ **Copy these credentials now!** Share securely with the new admin.")

                                st.balloons()
                            else:
                                st.error(f"❌ {result['message']}")
                    else:
                        st.warning("⚠️ Please enter an email address")

        st.divider()

        # Detailed Admin Creation Section
        st.markdown("### 🔐 Detailed Admin Creation")

        password_option = st.radio(
            "Choose password method:",
            ["🎲 Generate Secure Password", "✏️ Set Custom Password"],
            help="Auto-generated passwords are more secure and meet all requirements"
        )

        with st.form("add_admin_form"):
            col_form1, col_form2 = st.columns(2)

            with col_form1:
                new_email = st.text_input("📧 Admin Email", placeholder="newadmin@reminder.com")

                if password_option == "🎲 Generate Secure Password":
                    # Generate password button
                    generate_btn = st.form_submit_button("🎲 Generate New Password", type="secondary")

                    if generate_btn or 'generated_password' not in st.session_state:
                        st.session_state.generated_password = generate_secure_password()

                    # Display generated password
                    generated_pwd = st.session_state.get('generated_password', '')
                    st.text_input(
                        "🔑 Generated Password",
                        value=generated_pwd,
                        disabled=True,
                        help="This password will be used for the new admin account"
                    )

                    # Copy-friendly display
                    if generated_pwd:
                        st.code(f"Password: {generated_pwd}", language=None)
                        st.success("✅ Secure password generated! Copy it before creating the account.")

                    new_password = generated_pwd
                    confirm_password = generated_pwd

                else:
                    new_password = st.text_input("🔒 Password", type="password", placeholder="Minimum 8 characters")
                    confirm_password = st.text_input("🔒 Confirm Password", type="password")

                    # Show password strength for custom passwords
                    if new_password:
                        strength = check_password_strength(new_password)
                        st.markdown(f"**Password Strength:** {strength['display']}")
                        if strength['feedback']:
                            st.info(f"💡 Missing: {', '.join(strength['feedback'])}")

            with col_form2:
                # Role selection (only primary admin can create other primary admins)
                if current_user.get('role') == 'primary_admin':
                    role_options = ["admin", "primary_admin"]
                    role_help = "Primary admins can manage all users and settings"
                else:
                    role_options = ["admin"]
                    role_help = "You can only create standard admin accounts"

                new_role = st.selectbox("👑 Role", role_options, help=role_help)

                st.markdown("**Permissions Preview:**")
                if new_role == "primary_admin":
                    st.markdown("✅ Manage users\n✅ Lock/unlock accounts\n✅ View logs\n✅ System administration")
                else:
                    st.markdown("❌ Manage users\n❌ Lock/unlock accounts\n✅ View logs\n❌ System administration")

            # Password requirements (only show for custom passwords)
            if password_option == "✏️ Set Custom Password":
                st.markdown("**Password Requirements:**")
                st.markdown("• Minimum 8 characters\n• Include uppercase and lowercase letters\n• Include at least one number\n• Special characters recommended")

            add_admin_submitted = st.form_submit_button("➕ Create Admin Account", type="primary")

            if add_admin_submitted:
                if new_email and new_password and confirm_password:
                    if new_password != confirm_password:
                        st.error("❌ Passwords do not match!")
                    elif len(new_password) < 8:
                        st.error("❌ Password must be at least 8 characters long!")
                    elif new_email in credentials:
                        st.error("❌ Admin with this email already exists!")
                    else:
                        result = add_new_admin(new_email, new_password, new_role, current_admin)
                        if result["success"]:
                            st.success(f"✅ {result['message']}")

                            # Display credentials for the administrator
                            st.markdown("### 📋 **New Admin Credentials Created**")
                            st.markdown(f"**Email:** {new_email}")
                            st.markdown(f"**Role:** {new_role.replace('_', ' ').title()}")

                            # Show password in a secure way
                            with st.expander("🔑 Click to view password (copy and share securely)", expanded=False):
                                st.code(f"Password: {new_password}")
                                st.warning("⚠️ **Important Security Notice:**")
                                st.markdown("• Copy this password immediately")
                                st.markdown("• Share it securely with the new admin")
                                st.markdown("• This password will not be shown again")
                                st.markdown("• Advise the new admin to change it after first login")

                            # Clear generated password from session
                            if 'generated_password' in st.session_state:
                                del st.session_state.generated_password

                            st.balloons()  # Celebration effect
                            time.sleep(3)
                            st.rerun()
                        else:
                            st.error(f"❌ {result['message']}")
                else:
                    if password_option == "🎲 Generate Secure Password" and not new_password:
                        st.warning("⚠️ Please generate a password first by clicking 'Generate New Password'")
                    else:
                        st.warning("⚠️ Please fill in all fields.")

    with tab3:
        st.subheader("✏️ Edit Admin Details")

        if not current_user.get('permissions', {}).get('manage_users') and current_user.get('role') != 'primary_admin':
            st.error("❌ You don't have permission to edit admin details.")
        else:
            # Select admin to edit
            admin_emails = list(credentials.keys())

            # Filter based on permissions
            if current_user.get('role') != 'primary_admin':
                # Regular admins can only edit themselves
                admin_emails = [current_admin]

            selected_admin = st.selectbox(
                "Select Admin to Edit",
                admin_emails,
                help="Primary admins can edit any admin, regular admins can only edit themselves"
            )

            if selected_admin:
                admin_data = credentials[selected_admin]

                st.markdown(f"**Editing:** {selected_admin}")
                st.markdown(f"**Role:** {admin_data.get('role', 'admin')}")
                st.markdown(f"**Status:** {admin_data.get('status', 'active')}")

                # Edit options
                edit_option = st.radio(
                    "What would you like to edit?",
                    ["Change Email Address", "Change Password", "View Details Only"]
                )

                if edit_option == "Change Email Address":
                    st.subheader("📧 Change Email Address")

                    with st.form("change_email_form"):
                        new_email = st.text_input(
                            "New Email Address",
                            placeholder="newemail@example.com",
                            help="Enter the new email address for this admin"
                        )

                        st.warning("⚠️ Changing email will require the admin to use the new email for login.")

                        change_email_submitted = st.form_submit_button("🔄 Change Email", type="primary")

                        if change_email_submitted:
                            if new_email:
                                result = change_admin_email(selected_admin, new_email, current_admin)
                                if result["success"]:
                                    st.success(f"✅ {result['message']}")
                                    st.info("🔄 Please refresh the page to see the changes.")
                                    time.sleep(2)
                                    st.rerun()
                                else:
                                    st.error(f"❌ {result['message']}")
                            else:
                                st.warning("⚠️ Please enter a new email address.")

                elif edit_option == "Change Password":
                    st.subheader("🔒 Change Password")

                    with st.form("change_password_form"):
                        new_password = st.text_input(
                            "New Password",
                            type="password",
                            placeholder="Enter new password (min 8 characters)",
                            help="Password must be at least 8 characters long"
                        )

                        confirm_password = st.text_input(
                            "Confirm New Password",
                            type="password",
                            placeholder="Confirm the new password"
                        )

                        st.markdown("**Password Requirements:**")
                        st.markdown("• Minimum 8 characters\n• Include uppercase and lowercase letters\n• Include at least one number")

                        change_password_submitted = st.form_submit_button("🔄 Change Password", type="primary")

                        if change_password_submitted:
                            if new_password and confirm_password:
                                if new_password != confirm_password:
                                    st.error("❌ Passwords do not match!")
                                elif len(new_password) < 8:
                                    st.error("❌ Password must be at least 8 characters long!")
                                else:
                                    result = change_admin_password(selected_admin, new_password, current_admin)
                                    if result["success"]:
                                        st.success(f"✅ {result['message']}")
                                        if selected_admin == current_admin:
                                            st.info("🔄 Your password has been changed. You may need to login again.")
                                    else:
                                        st.error(f"❌ {result['message']}")
                            else:
                                st.warning("⚠️ Please fill in both password fields.")

                else:  # View Details Only
                    st.subheader("👤 Admin Details")

                    col_detail1, col_detail2 = st.columns(2)

                    with col_detail1:
                        st.markdown("**Basic Information:**")
                        st.write(f"📧 **Email:** {selected_admin}")
                        st.write(f"👑 **Role:** {admin_data.get('role', 'admin')}")
                        st.write(f"🔄 **Status:** {admin_data.get('status', 'active')}")
                        st.write(f"🆔 **ID:** {admin_data.get('id', 'N/A')}")

                    with col_detail2:
                        st.markdown("**Activity Information:**")
                        created_at = admin_data.get('created_at', '')
                        if created_at:
                            created_date = datetime.fromisoformat(created_at).strftime("%Y-%m-%d %H:%M")
                            st.write(f"📅 **Created:** {created_date}")

                        created_by = admin_data.get('created_by', 'Unknown')
                        st.write(f"👤 **Created By:** {created_by}")

                        last_login = admin_data.get('last_login', '')
                        if last_login:
                            login_date = datetime.fromisoformat(last_login).strftime("%Y-%m-%d %H:%M")
                            st.write(f"🕐 **Last Login:** {login_date}")
                        else:
                            st.write("🕐 **Last Login:** Never")

                        attempts = admin_data.get('login_attempts', 0)
                        st.write(f"⚠️ **Failed Attempts:** {attempts}")

                    # Permissions display
                    st.markdown("**Permissions:**")
                    permissions = admin_data.get('permissions', {})
                    perm_text = ""
                    for perm, has_perm in permissions.items():
                        icon = "✅" if has_perm else "❌"
                        perm_display = perm.replace('_', ' ').title()
                        perm_text += f"{icon} {perm_display}\n"

                    st.markdown(perm_text)

    with tab4:
        st.subheader("👤 User Account Management")

        if not current_user.get('permissions', {}).get('manage_users'):
            st.error("❌ You don't have permission to manage user accounts.")
        else:
            # Load user accounts
            user_accounts = load_user_accounts()

            # User account management sub-tabs
            user_tab1, user_tab2, user_tab3 = st.tabs(["📋 View User Accounts", "👤 Account Details", "🔧 Account Actions"])

            with user_tab1:
                st.markdown("### 📋 **Registered User Accounts**")

                if user_accounts:
                    # Summary statistics
                    total_users = len(user_accounts)
                    active_users = len([u for u in user_accounts.values() if u.get('status') == 'active'])
                    locked_users = len([u for u in user_accounts.values() if u.get('locked_until')])

                    col_stat1, col_stat2, col_stat3 = st.columns(3)
                    with col_stat1:
                        st.metric("👥 Total Users", total_users)
                    with col_stat2:
                        st.metric("✅ Active Users", active_users)
                    with col_stat3:
                        st.metric("🔒 Locked Users", locked_users)

                    st.divider()

                    # User accounts table
                    for email, data in user_accounts.items():
                        with st.container():
                            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])

                            with col1:
                                status_icon = "✅" if data.get('status') == 'active' else "❌"
                                locked_icon = "🔒" if data.get('locked_until') else ""
                                st.markdown(f"**{status_icon} {email}** {locked_icon}")
                                st.markdown(f"*User ID: {data.get('id', 'N/A')[:8]}...*")

                            with col2:
                                status = data.get('status', 'unknown')
                                st.markdown(f"**Status:** {status.title()}")
                                created_date = data.get('created_at', '')
                                if created_date:
                                    date_obj = datetime.fromisoformat(created_date)
                                    st.markdown(f"**Created:** {date_obj.strftime('%Y-%m-%d')}")

                            with col3:
                                last_login = data.get('last_login')
                                if last_login:
                                    login_obj = datetime.fromisoformat(last_login)
                                    st.markdown(f"**Last Login:**")
                                    st.markdown(f"{login_obj.strftime('%Y-%m-%d %H:%M')}")
                                else:
                                    st.markdown("**Last Login:**")
                                    st.markdown("Never")

                            with col4:
                                attempts = data.get('login_attempts', 0)
                                if attempts > 0:
                                    st.markdown(f"**Failed:**")
                                    st.markdown(f"{attempts}/5")
                                else:
                                    st.markdown("**Status:**")
                                    st.markdown("Good")

                            st.divider()
                else:
                    st.info("👤 No user accounts registered yet.")
                    st.markdown("Users can create accounts using the 'Create Account' option on the login page.")

            with user_tab2:
                st.markdown("### 👤 **User Account Details**")

                if user_accounts:
                    selected_user = st.selectbox("Select user account:", list(user_accounts.keys()))

                    if selected_user:
                        user_data = user_accounts[selected_user]

                        # Display user information
                        col_info1, col_info2 = st.columns(2)

                        with col_info1:
                            st.markdown("**Account Information:**")
                            st.markdown(f"📧 **Email:** {selected_user}")
                            st.markdown(f"🆔 **User ID:** {user_data.get('id', 'N/A')}")
                            st.markdown(f"👤 **Role:** {user_data.get('role', 'user').title()}")
                            st.markdown(f"📊 **Status:** {user_data.get('status', 'unknown').title()}")

                        with col_info2:
                            st.markdown("**Activity Information:**")
                            created_at = user_data.get('created_at')
                            if created_at:
                                created_obj = datetime.fromisoformat(created_at)
                                st.markdown(f"📅 **Created:** {created_obj.strftime('%Y-%m-%d %H:%M:%S')}")

                            last_login = user_data.get('last_login')
                            if last_login:
                                login_obj = datetime.fromisoformat(last_login)
                                st.markdown(f"🔑 **Last Login:** {login_obj.strftime('%Y-%m-%d %H:%M:%S')}")
                            else:
                                st.markdown("🔑 **Last Login:** Never")

                            st.markdown(f"🚫 **Failed Attempts:** {user_data.get('login_attempts', 0)}/5")

                            locked_until = user_data.get('locked_until')
                            if locked_until:
                                locked_obj = datetime.fromisoformat(locked_until)
                                if datetime.now() < locked_obj:
                                    st.markdown(f"🔒 **Locked Until:** {locked_obj.strftime('%Y-%m-%d %H:%M:%S')}")
                                else:
                                    st.markdown("🔒 **Lock Status:** Expired (will unlock on next login)")
                            else:
                                st.markdown("🔒 **Lock Status:** Not locked")
                else:
                    st.info("👤 No user accounts to display.")

            with user_tab3:
                st.markdown("### 🔧 **Account Actions**")

                if user_accounts:
                    action_user = st.selectbox("Select user for actions:", list(user_accounts.keys()), key="action_user")

                    if action_user:
                        user_data = user_accounts[action_user]
                        current_status = user_data.get('status', 'active')

                        st.markdown(f"**Selected User:** {action_user}")
                        st.markdown(f"**Current Status:** {current_status.title()}")

                        # Action buttons
                        col_action1, col_action2, col_action3 = st.columns(3)

                        with col_action1:
                            if current_status == 'active':
                                if st.button("🚫 Deactivate Account", type="secondary"):
                                    result = update_user_status(action_user, "inactive", current_admin)
                                    if result["success"]:
                                        st.success(f"✅ {result['message']}")
                                        st.rerun()
                                    else:
                                        st.error(f"❌ {result['message']}")
                            else:
                                if st.button("✅ Activate Account", type="primary"):
                                    result = update_user_status(action_user, "active", current_admin)
                                    if result["success"]:
                                        st.success(f"✅ {result['message']}")
                                        st.rerun()
                                    else:
                                        st.error(f"❌ {result['message']}")

                        with col_action2:
                            if st.button("🔓 Unlock Account", help="Remove account lock and reset failed attempts"):
                                # Unlock account by clearing lock and attempts
                                user_accounts[action_user]["locked_until"] = None
                                user_accounts[action_user]["login_attempts"] = 0
                                if save_user_accounts(user_accounts):
                                    log_admin_activity(current_admin, "user_account_unlocked", {"email": action_user})
                                    st.success("✅ Account unlocked successfully!")
                                    st.rerun()
                                else:
                                    st.error("❌ Failed to unlock account")

                        with col_action3:
                            if st.button("🗑️ Delete Account", type="secondary"):
                                st.warning("⚠️ This action cannot be undone!")
                                if st.button("🗑️ Confirm Delete", type="secondary"):
                                    result = delete_user_account(action_user, current_admin)
                                    if result["success"]:
                                        st.success(f"✅ {result['message']}")
                                        st.rerun()
                                    else:
                                        st.error(f"❌ {result['message']}")

                        # Reset password option
                        st.divider()
                        st.markdown("**🔒 Password Reset**")
                        st.info("Password reset functionality requires manual intervention. Contact the user to create a new account or implement password reset via email.")
                else:
                    st.info("👤 No user accounts available for actions.")

    with tab5:
        st.subheader("📧 Email Account Management")

        if not current_user.get('permissions', {}).get('manage_users'):
            st.error("❌ You don't have permission to manage email accounts.")
        else:
            # Load email accounts
            email_accounts = load_email_accounts()

            # Email Management sub-tabs
            email_tab1, email_tab2, email_tab3 = st.tabs(["📋 View Email Accounts", "➕ Add Email Account", "🔧 Manage Accounts"])

            with email_tab1:
                st.markdown("### 📋 **Current Email Accounts**")

                if email_accounts:
                    for email, data in email_accounts.items():
                        with st.container():
                            col1, col2, col3, col4 = st.columns([3, 2, 1, 1])

                            with col1:
                                default_badge = " 🌟 (Default)" if data.get('is_default') else ""
                                st.markdown(f"**📧 {email}**{default_badge}")
                                st.markdown(f"*{data.get('display_name', 'No display name')}*")

                            with col2:
                                status = data.get('status', 'active')
                                status_color = "🟢" if status == 'active' else "🔴"
                                st.markdown(f"**Status:** {status_color} {status.title()}")
                                st.markdown(f"**Sent:** {data.get('total_sent', 0)} emails")

                            with col3:
                                added_date = data.get('added_at', '')
                                if added_date:
                                    date_obj = datetime.fromisoformat(added_date)
                                    st.markdown(f"**Added:**")
                                    st.markdown(f"{date_obj.strftime('%Y-%m-%d')}")

                            with col4:
                                added_by = data.get('added_by', 'Unknown')
                                st.markdown(f"**By:**")
                                st.markdown(f"{added_by.split('@')[0]}")

                            st.divider()
                else:
                    st.info("📭 No email accounts configured yet. Add your first email account to start sending reminders!")

            with email_tab2:
                st.markdown("### ➕ **Add New Email Account**")

                with st.form("add_email_form"):
                    col_email1, col_email2 = st.columns(2)

                    with col_email1:
                        new_email = st.text_input("📧 Email Address*", placeholder="your.email@gmail.com")
                        new_display_name = st.text_input("👤 Display Name*", placeholder="Your Name or Department")

                    with col_email2:
                        new_password = st.text_input("🔒 App Password*", type="password",
                                                   placeholder="Gmail App Password (16 characters)")
                        is_default = st.checkbox("🌟 Set as Default Email",
                                                help="This email will be used by default for sending reminders")

                    # Instructions for Gmail App Password
                    with st.expander("ℹ️ How to get Gmail App Password", expanded=False):
                        st.markdown("""
                        **Steps to create Gmail App Password:**
                        1. Go to your Google Account settings
                        2. Select **Security** → **2-Step Verification** (must be enabled)
                        3. Go to **App passwords**
                        4. Select **Mail** and **Other (Custom name)**
                        5. Enter "Reminder System" as the name
                        6. Copy the 16-character password generated
                        7. Use this password in the form above

                        **Note:** Regular Gmail passwords won't work. You need an App Password.
                        """)

                    # Test connection option
                    test_connection = st.checkbox("🧪 Test connection before saving", value=True)

                    add_email_submitted = st.form_submit_button("➕ Add Email Account", type="primary")

                    if add_email_submitted:
                        if new_email and new_password and new_display_name:
                            # Test connection if requested
                            if test_connection:
                                with st.spinner("🧪 Testing email connection..."):
                                    test_result = test_email_account(new_email, new_password)

                                if not test_result["success"]:
                                    st.error(f"❌ Connection test failed: {test_result['message']}")
                                    st.info("💡 Please check your email and app password, then try again.")
                                    st.stop()
                                else:
                                    st.success("✅ Email connection test successful!")

                            # Add the email account
                            result = add_email_account(new_email, new_password, new_display_name, is_default, current_admin)

                            if result["success"]:
                                st.success(f"✅ {result['message']}")
                                st.balloons()
                                time.sleep(2)
                                st.rerun()
                            else:
                                st.error(f"❌ {result['message']}")
                        else:
                            st.warning("⚠️ Please fill in all required fields.")

            with email_tab3:
                st.markdown("### 🔧 **Manage Email Accounts**")

                if email_accounts:
                    selected_email = st.selectbox("Select email account to manage:", list(email_accounts.keys()))

                    if selected_email:
                        account_data = email_accounts[selected_email]

                        # Account management options
                        management_option = st.radio(
                            "What would you like to do?",
                            ["📝 Edit Account", "🧪 Test Connection", "🗑️ Delete Account"]
                        )

                        if management_option == "📝 Edit Account":
                            with st.form("edit_email_form"):
                                edit_display_name = st.text_input("Display Name", value=account_data.get('display_name', ''))
                                edit_password = st.text_input("New App Password (leave blank to keep current)", type="password")
                                edit_is_default = st.checkbox("Set as Default", value=account_data.get('is_default', False))
                                edit_status = st.selectbox("Status", ["active", "inactive"],
                                                         index=0 if account_data.get('status') == 'active' else 1)

                                update_submitted = st.form_submit_button("💾 Update Account", type="primary")

                                if update_submitted:
                                    updates = {
                                        "display_name": edit_display_name,
                                        "is_default": edit_is_default,
                                        "status": edit_status
                                    }

                                    if edit_password:
                                        updates["password"] = edit_password

                                    result = update_email_account(selected_email, updates, current_admin)

                                    if result["success"]:
                                        st.success(f"✅ {result['message']}")
                                        st.rerun()
                                    else:
                                        st.error(f"❌ {result['message']}")

                        elif management_option == "🧪 Test Connection":
                            if st.button("🧪 Test Email Connection", type="primary"):
                                with st.spinner("Testing connection..."):
                                    password = decrypt_password(account_data["password"])
                                    test_result = test_email_account(selected_email, password)

                                if test_result["success"]:
                                    st.success(f"✅ {test_result['message']}")
                                else:
                                    st.error(f"❌ {test_result['message']}")

                        elif management_option == "🗑️ Delete Account":
                            st.warning(f"⚠️ Are you sure you want to delete **{selected_email}**?")
                            st.markdown("This action cannot be undone.")

                            if st.button("🗑️ Confirm Delete", type="secondary"):
                                result = delete_email_account(selected_email, current_admin)

                                if result["success"]:
                                    st.success(f"✅ {result['message']}")
                                    st.rerun()
                                else:
                                    st.error(f"❌ {result['message']}")
                else:
                    st.info("📭 No email accounts to manage. Add an email account first.")

    with tab6:
        st.subheader("📊 System Analytics & Statistics")

        # Load all account data
        admin_accounts = credentials
        user_accounts = load_user_accounts()

        # Admin Statistics
        st.markdown("### 👑 **Admin Account Statistics**")
        total_admins = len(admin_accounts)
        active_admins = len([u for u in admin_accounts.values() if u.get("status") == "active"])
        locked_admins = total_admins - active_admins
        primary_admins = len([u for u in admin_accounts.values() if u.get("role") == "primary_admin"])

        col_admin1, col_admin2, col_admin3, col_admin4 = st.columns(4)
        with col_admin1:
            st.metric("👑 Total Admins", total_admins)
        with col_admin2:
            st.metric("✅ Active Admins", active_admins)
        with col_admin3:
            st.metric("🔒 Locked Admins", locked_admins)
        with col_admin4:
            st.metric("👑 Primary Admins", primary_admins)

        st.divider()

        # User Statistics
        st.markdown("### 👤 **User Account Statistics**")
        total_users = len(user_accounts)
        active_users = len([u for u in user_accounts.values() if u.get("status") == "active"])
        locked_users = len([u for u in user_accounts.values() if u.get("locked_until")])
        never_logged_in = len([u for u in user_accounts.values() if not u.get("last_login")])

        col_user1, col_user2, col_user3, col_user4 = st.columns(4)
        with col_user1:
            st.metric("👥 Total Users", total_users)
        with col_user2:
            st.metric("✅ Active Users", active_users)
        with col_user3:
            st.metric("🔒 Locked Users", locked_users)
        with col_user4:
            st.metric("🆕 Never Logged In", never_logged_in)

        st.divider()

        # Combined Statistics
        st.markdown("### 📊 **System Overview**")
        total_accounts = total_admins + total_users
        total_active = active_admins + active_users

        col_sys1, col_sys2, col_sys3 = st.columns(3)
        with col_sys1:
            st.metric("🌐 Total Accounts", total_accounts)
        with col_sys2:
            st.metric("✅ Total Active", total_active)
        with col_sys3:
            if total_accounts > 0:
                active_percentage = (total_active / total_accounts) * 100
                st.metric("📈 Active Rate", f"{active_percentage:.1f}%")
            else:
                st.metric("📈 Active Rate", "0%")

        # Recent activity summary
        st.subheader("📈 Recent Activity Summary")

        # Login activity chart (simplified)
        login_data = []
        for email, user_data in credentials.items():
            last_login = user_data.get('last_login')
            if last_login:
                login_data.append({
                    'User': email,
                    'Last Login': datetime.fromisoformat(last_login).strftime("%Y-%m-%d %H:%M"),
                    'Status': user_data.get('status', 'active'),
                    'Role': user_data.get('role', 'admin'),
                    'Failed Attempts': user_data.get('login_attempts', 0)
                })

        if login_data:
            import pandas as pd
            df = pd.DataFrame(login_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No login activity data available")

    with tab7:
        if current_user.get('permissions', {}).get('view_logs'):
            st.subheader("📝 Admin Activity Logs")

            # Load and display logs
            if os.path.exists(ADMIN_LOGS_FILE):
                with open(ADMIN_LOGS_FILE, 'r') as f:
                    logs = json.load(f)

                # Filter options
                col_log1, col_log2, col_log3 = st.columns(3)
                with col_log1:
                    log_limit = st.selectbox("Show entries", [10, 25, 50, 100])
                with col_log2:
                    action_filter = st.selectbox("Filter by action", ["All"] + list(set([log.get('action', '') for log in logs])))
                with col_log3:
                    admin_filter = st.selectbox("Filter by admin", ["All"] + list(set([log.get('admin_email', '') for log in logs])))

                # Apply filters
                filtered_logs = logs[-log_limit:]  # Get recent logs
                if action_filter != "All":
                    filtered_logs = [log for log in filtered_logs if log.get('action') == action_filter]
                if admin_filter != "All":
                    filtered_logs = [log for log in filtered_logs if log.get('admin_email') == admin_filter]

                # Display logs
                for log in reversed(filtered_logs):  # Show newest first
                    timestamp = datetime.fromisoformat(log['timestamp']).strftime("%Y-%m-%d %H:%M:%S")
                    action = log.get('action', 'unknown')
                    admin = log.get('admin_email', 'unknown')
                    details = log.get('details', {})

                    # Action icons
                    action_icons = {
                        'login_success': '✅',
                        'login_failed': '❌',
                        'logout': '🚪',
                        'admin_created': '➕',
                        'user_locked': '🔒',
                        'user_unlocked': '🔓',
                        'admin_deleted': '🗑️',
                        'attempts_reset': '🔄'
                    }

                    icon = action_icons.get(action, '📝')

                    with st.expander(f"{icon} {timestamp} - {action} by {admin}"):
                        st.json(details)

                # Clear logs button
                if st.button("🗑️ Clear All Logs", type="secondary"):
                    with open(ADMIN_LOGS_FILE, 'w') as f:
                        json.dump([], f)
                    st.success("✅ All logs cleared!")
                    st.rerun()
            else:
                st.info("No activity logs found")
        else:
            st.error("❌ You don't have permission to view activity logs.")
