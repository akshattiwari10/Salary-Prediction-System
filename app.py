import streamlit as st
import numpy as np 
import joblib 
import pandas as pd 

scaler = joblib.load("scaler.pkl")
model = joblib.load("Salary_prediction_model.pkl")
features= joblib.load("model_features.pkl")

st.title("💼 Salary Prediction System")
st.write("Predict salary based on personal and professional details")

#user inputs
age = st.number_input("Age", min_value=18 , max_value=65 , value=25)
gender = st.selectbox("Gender ", ["Male", "Female"])
education = st.selectbox("Education Level" , ["Bachelors" , "Masters", "PhD"])
job_title = st.text_input("Job_title", "Data Scientist")
experience = st.number_input("Experience(Years)", min_value=0 , max_value=40 , value=2)

#predict button
if st.button("Predict Salary"):
    input_data ={
        "Age": age,
        "Gender": gender,
        "Education": education,
        "Job Title": job_title,
        "Years of Experience": experience
    }

    input_df = pd.DataFrame([input_data])

    #one hot encoded
    input_encoded=pd.get_dummies(input_df)

    #align with training features 
    input_encoded= input_encoded.reindex(
        columns=features, 
        fill_value=0
    )

    #scale numerical features 
    input_encoded[['Age', 'Years of Experience']] = scaler.transform(
        input_encoded[['Age', 'Years of Experience']]
    )


    # Predict salary
    prediction = model.predict(input_encoded)[0]

    # Output result
    st.success(f"💰 Predicted Salary: ₹ {prediction:,.2f}")