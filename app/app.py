# ==================================================
# 🛒 SMART RECOMMENDER — FINAL PRODUCTION VERSION
# ==================================================
import streamlit as st
import pandas as pd
import numpy as np
import pickle
import os
import hashlib
from datetime import datetime, timedelta
import urllib.request

# ==================================================
# 📱 PAGE CONFIG
# ==================================================
st.set_page_config(
    page_title="Smart Recommender",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
.block-container {padding-top: 1rem;}
button {width: 100%;}
</style>
""", unsafe_allow_html=True)

# ==================================================
# 🔐 PASSWORD UTILS
# ==================================================
def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

# ==================================================
# 📂 DATA FOLDERS
# ==================================================
os.makedirs("data", exist_ok=True)
os.makedirs("models", exist_ok=True)

# ==================================================
# ⬇️ AUTO-DOWNLOAD DATASETS (STREAMLIT CLOUD SAFE)
# ==================================================
DATA_FILES = {
    "data/Electronics.csv.gz":
        "https://github.com/kaveeshaDivyanjalee/Smart-Recommender/releases/download/v1.0/Electronics.csv.gz",

    "data/asin_title_map.csv":
        "https://github.com/kaveeshaDivyanjalee/Smart-Recommender/releases/download/v1.0/asin_title_map.csv",

    "data/asin_image_map.csv":
        "https://github.com/kaveeshaDivyanjalee/Smart-Recommender/releases/download/v1.0/asin_image_map.csv",

    "models/final_svd_model.pkl":
        "https://github.com/kaveeshaDivyanjalee/Smart-Recommender/releases/download/v1.0/final_svd_model.pkl",
}

def ensure_data():
    os.makedirs("data", exist_ok=True)
    os.makedirs("models", exist_ok=True)

    for path, url in DATA_FILES.items():
        if not os.path.exists(path):
            st.info(f"⬇️ Downloading {os.path.basename(path)}...")
            urllib.request.urlretrieve(url, path)



# ==================================================
# 👥 USER STORAGE
# ==================================================
USERS_FILE = "data/users.csv"

if not os.path.exists(USERS_FILE):
    pd.DataFrame(
        columns=["username", "password", "role", "created_at"]
    ).to_csv(USERS_FILE, index=False)

users_df = pd.read_csv(USERS_FILE)

def save_users():
    users_df.to_csv(USERS_FILE, index=False)

def add_user(username, password, role="user"):
    global users_df
    users_df = pd.concat([users_df, pd.DataFrame([{
        "username": username,
        "password": hash_pw(password),
        "role": role,
        "created_at": datetime.now()
    }])], ignore_index=True)
    save_users()

# ==================================================
# 👑 AUTO‑CREATE ADMIN (STREAMLIT CLOUD SAFE)
# ==================================================
if "admin" not in users_df.username.values:
    add_user("admin", "admin123", role="admin")

# ==================================================
# 🔐 AUTH STATE
# ==================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ==================================================
# 🔐 LOGIN / SIGNUP / RESET
# ==================================================
if not st.session_state.logged_in:
    st.title("🔐 Smart Recommender")

    tab1, tab2, tab3 = st.tabs(["Login", "Sign Up", "Reset Password"])

    # ---------- LOGIN ----------
    with tab1:
        with st.form("login"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            ok = st.form_submit_button("Login")

            if ok:
                row = users_df[
                    (users_df.username == u) &
                    (users_df.password == hash_pw(p))
                ]
                if not row.empty:
                    st.session_state.logged_in = True
                    st.session_state.username = u
                    st.session_state.role = row.iloc[0].role
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials")

    # ---------- SIGN UP ----------
    with tab2:
        with st.form("signup"):
            su = st.text_input("New Username")
            sp = st.text_input("New Password", type="password")
            create = st.form_submit_button("Create Account")

            if create:
                if su in users_df.username.values:
                    st.error("❌ Username already exists")
                else:
                    add_user(su, sp)
                    st.success("✅ Account created — please login")

    # ---------- RESET PASSWORD ----------
    with tab3:
        with st.form("reset"):
            ru = st.text_input("Username")
            rp = st.text_input("New Password", type="password")
            reset = st.form_submit_button("Reset Password")

            if reset:
                if ru not in users_df.username.values:
                    st.error("❌ User not found")
                else:
                    users_df.loc[
                        users_df.username == ru, "password"
                    ] = hash_pw(rp)
                    save_users()
                    st.success("✅ Password reset successful")

    st.stop()

# ==================================================
# 🚪 LOGOUT
# ==================================================
st.sidebar.success(f"Logged in as {st.session_state.username}")
if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()

username = st.session_state.username
is_admin = st.session_state.role == "admin"

# ==================================================
# ⚡ LOAD DATA (CACHED)
# ==================================================
@st.cache_data(show_spinner=False)
def load_data():
    df = pd.read_csv("data/Electronics.csv.gz", compression="gzip")
    titles = pd.read_csv("data/asin_title_map.csv")
    images = pd.read_csv("data/asin_image_map.csv")
    with open("models/final_svd_model.pkl", "rb") as f:
        model = pickle.load(f)
    return df, titles, images, model
ensure_data()

df, titles, images, model = load_data()

asin_to_title = dict(zip(titles.asin, titles.title))
asin_to_image = dict(zip(images.asin, images.image))

def get_title(a): return asin_to_title.get(a, a)
def get_image(a): return asin_to_image.get(a, "https://via.placeholder.com/300")

# ==================================================
# 🧠 MODEL
# ==================================================
users = model["users"]
items = model["items"]
U = model["user_factors"]
V = model["item_factors"]

popularity = df.groupby("parent_asin")["rating"].mean()

# ==================================================
# 💾 FEEDBACK STORAGE
# ==================================================
FEEDBACK_FILE = "data/user_feedback.csv"

if not os.path.exists(FEEDBACK_FILE):
    pd.DataFrame(
        columns=["user", "item", "feedback", "timestamp"]
    ).to_csv(FEEDBACK_FILE, index=False)

feedback_df = pd.read_csv(FEEDBACK_FILE)

def save_feedback(user, item, value):
    global feedback_df
    feedback_df = pd.concat([feedback_df, pd.DataFrame([{
        "user": user,
        "item": item,
        "feedback": value,
        "timestamp": datetime.now()
    }])], ignore_index=True)
    feedback_df.to_csv(FEEDBACK_FILE, index=False)

# ==================================================
# 🎯 RECOMMENDER
# ==================================================
def recommend(user, n=8):
    disliked = feedback_df[
        (feedback_df.user == user) & (feedback_df.feedback == -1)
    ].item.tolist()

    if user in users:
        scores = pd.Series(np.dot(U[users.get_loc(user)], V), index=items)
    else:
        scores = popularity.reindex(items).fillna(popularity.mean())

    for d in disliked:
        if d in items:
            scores.loc[d] = -999

    return scores.sort_values(ascending=False).head(n).index

# ==================================================
# 🛒 USER VIEW
# ==================================================
if not is_admin:
    st.title("🛒 Recommended for You")

    for asin in recommend(username):
        c1, c2 = st.columns([1, 3])
        with c1:
            st.image(get_image(asin), width='stretch')
        with c2:
            st.subheader(get_title(asin))
            l, d = st.columns(2)
            if l.button("👍 Like", key=f"l_{asin}"):
                save_feedback(username, asin, 1)
                st.rerun()
            if d.button("👎 Dislike", key=f"d_{asin}"):
                save_feedback(username, asin, -1)
                st.rerun()
        st.divider()

# ==================================================
# 📊 ADMIN DASHBOARD (LOCKED)
# ==================================================
if is_admin:
    st.title("📊 Admin Dashboard")

    st.metric("Total Users", users_df.username.nunique())
    st.metric(
        "7‑Day Retention",
        feedback_df[
            pd.to_datetime(feedback_df.timestamp)
            > datetime.now() - timedelta(days=7)
        ].user.nunique()
    )

    st.subheader("👑 User Management")
    st.dataframe(users_df)

    target = st.selectbox("Select User", users_df.username)
    if st.button("Promote / Demote"):
        idx = users_df.username == target
        users_df.loc[idx, "role"] = (
            "admin" if users_df.loc[idx, "role"].values[0] == "user" else "user"
        )
        save_users()
        st.success("✅ Role updated")
        st.rerun()

    st.subheader("👥 User → Item Feedback")
    table = feedback_df.copy()
    table["Product"] = table.item.map(get_title)
    table["Action"] = table.feedback.map({1: "Like", -1: "Dislike"})
    st.dataframe(
        table[["user", "Product", "Action", "timestamp"]]
        .sort_values("timestamp", ascending=False)
    )

# ==================================================
# FOOTER
# ==================================================
st.caption("🚀 Developed By Kaveesha Divyanjalee")