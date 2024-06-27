import os
import psycopg2
from dotenv import load_dotenv
import streamlit as st
import bcrypt
import pandas as pd

# Load environment variables from the .env file
load_dotenv()

# Connect to the PostgreSQL database
conn = psycopg2.connect(
    PG_HOST = os.getenv('PG_HOST', st.secrets.get('PG_HOST')),
    PG_DATABASE = os.getenv('PG_DATABASE', st.secrets.get('PG_DATABASE')),
    PG_USER = os.getenv('PG_USER', st.secrets.get('PG_USER')),
    PG_PASSWORD = os.getenv('PG_PASSWORD', st.secrets.get('PG_PASSWORD'))
)

# Verify user credentials
def authenticate_user(username, password):
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
    result = cursor.fetchone()
    cursor.close()
    if result and bcrypt.checkpw(password.encode(), result[0].encode()):
        return True
    return False

# Function to store data in the database
def store_data(username, password):
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
    conn.commit()
    cursor.close()

# Function to retrieve data from the database
def get_data():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    data = cursor.fetchall()
    cursor.close()
    return data

def get_user_id(username):
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
    data = cursor.fetchone()
    cursor.close()
    return data[0]

def get_paipu_data(userID):
    cursor = conn.cursor()
    cursor.execute("SELECT userName, paipuDate, paipuCode FROM paipu WHERE streamerID = %s", (userID,))
    data = cursor.fetchall()
    cursor.close()
    return data

def get_schedule_data(userID):
    cursor = conn.cursor()
    cursor.execute("SELECT userName, scheduleDate, scheduleContent FROM schedule WHERE streamerID = %s", (userID,))
    data = cursor.fetchall()
    cursor.close()
    return data

def get_question_data(userID):
    cursor = conn.cursor()
    cursor.execute("SELECT userName, questionDate, questionContent FROM question WHERE streamerID = %s", (userID,))
    data = cursor.fetchall()
    cursor.close()
    return data

# Function to delete data from the database
def delete_data(username):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE username = %s", (username,))
    conn.commit()
    cursor.close()

# Function to update password in the database
def update_password(username, password):
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET password = %s WHERE username = %s", (hashed_password, username))
    conn.commit()
    cursor.close()

# Define function for Home page
def home_page():
    st.title("일싹이 페이지에 오신걸 환영해요!")
    login_page()
    st.write("문의는 1041489@gmail.com으로 해주세요!")

# Define function for Profile page
def document_page():
    with open('ilssak-streamlit/readme.md', 'r', encoding='utf-8') as file:
        markdown_content = file.read()
    st.markdown(markdown_content, unsafe_allow_html=True)

# login page
def login_page():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user_id = None

    if st.session_state.logged_in:
        return st.session_state.user_id

    st.write("스트리머 페이지를 사용하려면 로그인해야해요!!")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if authenticate_user(username, password):
            st.session_state.logged_in = True
            st.session_state.user_id = get_user_id(username)
            st.write(f"{username} 님, 어서와!")
            return st.session_state.user_id
        else:
            st.write("로그인 실패.. 😭")
            return False

# Define function for Streamer page
def streamer_page():
    userID = st.session_state.user_id
    # if login is successful
    if userID:
        # 탭 생성 : 첫번째 탭의 이름은 Tab A 로, Tab B로 표시합니다. 
        tab1, tab2, tab3 = st.tabs(['패보' , '스케줄', '질문'])

        with tab1:
            paipu_data = get_paipu_data(userID)
            df = pd.DataFrame(paipu_data, columns=['등록한 시청자', '등록한 일시', '등록한 패보'])
            st.write(df)

        with tab2:
            schedule_data = get_schedule_data(userID)
            df = pd.DataFrame(schedule_data, columns=['등록한 시청자', '등록한 일시', '등록한 스케줄'])
            st.write(df)

        with tab3:
            question_data = get_question_data(userID)
            df = pd.DataFrame(question_data, columns=['등록한 시청자', '등록한 일시', '등록한 질문'])
            st.write(df)

    else:
        st.write("로그인을 해주셔야 볼 수 있어요 😢")

# Create sidebar menu
menu_selection = st.sidebar.radio("Menu", ["Home", "Document", "Streamer"])

# Display selected page
if menu_selection == "Home":
    home_page()
elif menu_selection == "Document":
    document_page()
elif menu_selection == "Streamer":
    streamer_page()
