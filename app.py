import streamlit as st
import pandas as pd
import joblib

from db import (
    register_user,
    login_user,
    save_prediction,
    get_prediction_history,
    get_all_prediction_history
)

# -------------------------------------------------
# SESSION STATE (MUST BE FIRST)
# -------------------------------------------------
if "user" not in st.session_state:
    st.session_state.user = None

if "view" not in st.session_state:
    st.session_state.view = "predict"


# =================================================
# LOGIN / REGISTER PAGE
# =================================================
if st.session_state.user is None:
    st.title("💼 Salary Prediction System")
    st.write("User Authentication")

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        st.subheader("Login")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            user = login_user(email, password)
            if user:
                st.session_state.user = user
                st.success(f"Welcome {user['username']} 👋")
                st.rerun()
            else:
                st.error("Invalid email or password")

    with tab2:
        st.subheader("Register")
        username = st.text_input("Username")
        email = st.text_input("Email", key="reg_email")
        password = st.text_input("Password", type="password", key="reg_pw")

        if st.button("Register"):
            if register_user(username, email, password):
                st.success("Account created! Please login.")
            else:
                st.error("User already exists")

    st.stop()


# -------------------------------------------------
# LOAD MODEL FILES
# -------------------------------------------------
scaler = joblib.load("scaler4.pkl")
model = joblib.load("version4_model.pkl")
features = joblib.load("model_features4.pkl")


# -------------------------------------------------
# HEADER
# -------------------------------------------------
st.title("💼 Salary Prediction System")
st.write("Predict salary and explore insights")

# -------------------------------------------------
# USER INFO + LOGOUT
# -------------------------------------------------
colA, colB = st.columns([6, 1])

with colA:
    st.write(f"👤 Logged in as: **{st.session_state.user['username']}**")

with colB:
    if st.button("🚪 Logout"):
        st.session_state.user = None
        st.session_state.view = "predict"
        st.rerun()



# -------------------------------------------------
# NAVIGATION
# -------------------------------------------------
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔮 Predict"):
        st.session_state.view = "predict"

with col2:
    if st.button("📜 History"):
        st.session_state.view = "history"

with col3:
    if st.button("📊 Analytics"):
        st.session_state.view = "analytics"

st.divider()

with st.expander("🔐 Admin Access"):
    admin_password = st.text_input("Admin password", type="password")
    if admin_password == "akshat@123":
        if st.button("Open Admin Analytics"):
            st.session_state.view = "admin"


# -------------------------------------------------
# INDUSTRY MAPPING
# -------------------------------------------------
def map_industry(job_title):
    title = job_title.lower()

    if any(x in title for x in ['software', 'developer', 'engineer', 'it']):
        return 'Tech'
    elif any(x in title for x in ['data', 'analyst', 'scientist']):
        return 'Data / Analytics'
    elif any(x in title for x in ['finance', 'accountant']):
        return 'Finance'
    elif any(x in title for x in ['marketing', 'seo']):
        return 'Marketing'
    elif any(x in title for x in ['sales']):
        return 'Sales'
    elif any(x in title for x in ['hr', 'recruit']):
        return 'HR'
    else:
        return 'Operations / Management'


# =================================================
# 🔮 PREDICTION VIEW
# =================================================
if st.session_state.view == "predict":

    st.subheader("🔮 Salary Prediction")

    age = st.number_input("Age", 18, 65, 25)
    gender = st.selectbox("Gender", ["Male", "Female"])
    education = st.selectbox("Education Level", ["Bachelors", "Masters", "PhD"])
    job_title = st.text_input("Job Title", "Data Scientist")
    experience = st.number_input("Years of Experience", 0, 40, 2)
    company_size = st.selectbox("Company Size", ["startup", "small", "medium", "large"])

    industry = map_industry(job_title)

    if st.button("Predict Salary"):
        input_data = {
            "Age": age,
            "Gender": gender,
            "Education Level": education,
            "Job Title": job_title,
            "Industry": industry,
            "Company_Size": company_size,
            "Years of Experience": experience
        }

        df = pd.DataFrame([input_data])
        df = pd.get_dummies(df)
        df = df.reindex(columns=features, fill_value=0)

        df[['Age', 'Years of Experience']] = scaler.transform(
            df[['Age', 'Years of Experience']]
        )

        prediction = model.predict(df)[0]

        save_prediction(
            {
                'age': age,
                'gender': gender,
                'education': education,
                'job_title': job_title,
                'industry': industry,
                'company_size': company_size,
                'experience_years': experience,
                'predicted_salary': float(prediction)
            },
            st.session_state.user['id']
        )

        st.success(f"💰 Predicted Salary: ₹ {prediction:,.2f}")


# =================================================
# 📜 HISTORY VIEW (USER)
# =================================================
if st.session_state.view == "history":

    st.subheader("📜 Your Prediction History")

    history = get_prediction_history(st.session_state.user['id'], limit=30)

    if history:
        st.dataframe(pd.DataFrame(history), use_container_width=True)
    else:
        st.info("No predictions yet.")


# =================================================
# 📊 ANALYTICS VIEW (USER)
# =================================================
if st.session_state.view == "analytics":

    st.subheader("📊 Your Analytics")

    history = get_prediction_history(st.session_state.user['id'], limit=200)

    if history:
        df = pd.DataFrame(history)

        st.bar_chart(df.groupby("industry")["predicted_salary"].mean())
        st.scatter_chart(df[["experience_years", "predicted_salary"]])
    else:
        st.info("Not enough data yet.")


# =================================================
# 🔐 ADMIN ANALYTICS
# =================================================
if st.session_state.view == "admin":

    st.subheader("🔐 Admin Analytics Dashboard")

    history = get_all_prediction_history(limit=1000)

    if history:
        df = pd.DataFrame(history)

        st.metric("Total Predictions", len(df))
        df['date'] = pd.to_datetime(df['created_at']).dt.date
        st.line_chart(df.groupby("date").size())
        st.bar_chart(df['job_title'].value_counts().head(10))
        st.bar_chart(df['company_size'].value_counts())
    else:
        st.warning("No data available.")
