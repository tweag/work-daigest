import datetime

import streamlit as st

from work_daigest.main import PROMPT_TEMPLATE, process_data

# Title and description
st.title("Work-dAIgest 📰")
st.subheader("Generate a summary of your work with AI")

# Sidebar for input
with st.sidebar:
    st.header("Configuration")
    email = st.text_input(
        "Email Address",
        help="Used to detect attendance in calendar events",
    )
    github_handle = st.text_input(
        "GitHub Handle",
        help="Used to fetch your GitHub activity: issues, PRs, commits.",
    )
    calendar_data = st.file_uploader("Upload Calendar .ics File", type=["ics"])
    lower_date = st.date_input(
        "Lower Date Limit", datetime.datetime.today() - datetime.timedelta(days=7)
    )
    lower_date = datetime.datetime.combine(lower_date, datetime.time.min)
    upper_date = st.date_input("Upper Date Limit", datetime.datetime.today())
    upper_date = datetime.datetime.combine(upper_date, datetime.time.max)
    model_options = ["claude3", "jurassic2", "llama2"]
    model_choice = st.selectbox(
        "Choose a model", model_options, help="Make sure you enable the model in AWS"
    )

# Button to trigger summary generation
# add magic light emoji
if st.button("Generate Summary 🪄"):
    if not all([email, github_handle, calendar_data]):
        st.error("Please fill out all required fields.")
    else:
        model_fn, calendar_data, github_data = process_data(
            calendar_data, github_handle, email, lower_date, upper_date, model_choice
        )
        st.info(
            f"Got {len(calendar_data)} calendar event(s) and {len(github_data)} GitHub event(s)."
        )
        st.success(f"Generating summary for {email} using {model_choice}...")
        summary = model_fn(
            prompt=PROMPT_TEMPLATE.format(
                calendar_data='\n'.join(calendar_data), github_data=github_data
            )
        )
        st.write(summary)
