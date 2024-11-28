import streamlit as st
from PIL import Image
from datetime import datetime
import json
import os

USER_DATA_FILE = "user_data.json"

def load_user_data():
    """Load user data from a file."""
    try:
        with open(USER_DATA_FILE, "r") as f:
            json_data = json.load(f)
            for username, user_data in json_data.items():
                user_data["profile"] = None  
            return json_data
    except FileNotFoundError:
        return {}

def save_user_data():
    """Save user data to a file."""
    with open(USER_DATA_FILE, "w") as f:
        json_data = {k: {**v, "profile": None} for k, v in st.session_state["users"].items()}
        json.dump(json_data, f)

if not os.path.exists("profile_pics"):
    os.makedirs("profile_pics")

if "users" not in st.session_state:
    st.session_state["users"] = load_user_data()
    st.session_state["auth_status"] = None

def authenticate(username, password):
    users = st.session_state["users"]
    return username in users and users[username]["password"] == password

def login():
    st.title("TaskRabbit - Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if authenticate(username, password):
            st.session_state["auth_status"] = username
            st.success(f"Welcome, {st.session_state['users'][username]['name']}!")
        else:
            st.error("Invalid username or password!")

def register():
    st.title("TaskRabbit - Register")
    name = st.text_input("Full Name")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Register"):
        users = st.session_state["users"]
        if username in users:
            st.error("Username already exists!")
        else:
            users[username] = {"name": name, "password": password, "profile": None, "tasks": []}
            save_user_data()
            st.success("User registered successfully! Please log in.")

def user_profile(username):
    st.title("User Profile")
    users = st.session_state["users"]
    profile_pic = users[username].get("profile")
    if profile_pic and os.path.exists(profile_pic):
        st.image(profile_pic, width=150, caption="Profile Picture")
    else:
        st.text("No picture uploaded.")
    
    uploaded_pic = st.file_uploader("Upload a Profile Picture", type=["png", "jpg", "jpeg"])
    if uploaded_pic:
        file_path = f"profile_pics/{username}_profile.jpg"
        with open(file_path, "wb") as f:
            f.write(uploaded_pic.getbuffer())
        users[username]["profile"] = file_path
        save_user_data()
        st.success("Profile picture updated!")

def manage_tasks(username):
    st.title("Task Management")
    users = st.session_state["users"]
    
    st.subheader("Create a New Task")
    task_title = st.text_input("Task Title")
    task_description = st.text_area("Task Description")
    task_deadline = st.date_input("Deadline", min_value=datetime.now().date())
    if st.button("Add Task"):
        task = {
            "title": task_title,
            "description": task_description,
            "deadline": str(task_deadline)
        }
        users[username]["tasks"].append(task)
        save_user_data()
        st.success("Task added successfully!")

    st.subheader("Your Tasks")
    for i, task in enumerate(users[username]["tasks"]):
        st.write(f"### Task {i + 1}: {task['title']}")
        st.write(f"**Description:** {task['description']}")
        st.write(f"**Deadline:** {task['deadline']}")
        if st.button(f"Delete Task {i + 1}", key=f"delete_{i}"):
            del users[username]["tasks"][i]
            save_user_data()
            st.success("Task deleted successfully!")
            st.experimental_rerun()

def main():
    if st.session_state["auth_status"]:
        username = st.session_state["auth_status"]
        st.sidebar.title(f"Welcome, {st.session_state['users'][username]['name']}!")
        page = st.sidebar.selectbox("Navigate", ["User Profile", "Manage Tasks", "Logout"])
        if page == "User Profile":
            user_profile(username)
        elif page == "Manage Tasks":
            manage_tasks(username)
        elif page == "Logout":
            st.session_state["auth_status"] = None
            st.sidebar.success("Logged out successfully!")
            st.experimental_rerun()
    else:
        action = st.sidebar.radio("Choose an action", ["Login", "Register"])
        if action == "Login":
            login()
        elif action == "Register":
            register()

if __name__ == "__main__":
    main()
