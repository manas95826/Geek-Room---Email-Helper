import streamlit as st
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time

# Add sidebar with instructions
with st.sidebar:
    st.header("How to Use")
    st.markdown("""
    ### Step 1: Prepare Your CSV File
    - Create a CSV file with required columns:
        - First name
        - Email
        - Company Name
    - Additional columns are allowed
    
    ### Step 2: Configure SMTP
    - For Gmail:
        1. Use `smtp.gmail.com` as server
        2. Use port `587`
        3. [Create an App Password](https://myaccount.google.com/apppasswords)
        4. Use your Gmail address and App Password
    
    ### Step 3: Upload and Verify
    - Upload your CSV file
    - Verify the preview shows correct data
    
    ### Step 4: Customize Email
    - Edit the email subject
    - Customize the message template
    - Use `{First name}` to personalize emails
    
    ### Step 5: Send Emails
    - Click 'Send Emails' button
    - Monitor progress in the main window
    - Wait for confirmation messages
    
    ### Tips
    - Test with a small list first
    - Check spam folder if emails not received
    - Keep message template professional
    """)

def send_email(smtp_server, smtp_port, sender_email, sender_password, recipient_email, subject, body, max_retries=3):
    for attempt in range(max_retries):
        try:
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = recipient_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(smtp_server, smtp_port, timeout=30) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(msg)
                return True
        except smtplib.SMTPServerDisconnected as e:
            if attempt == max_retries - 1:  # Last attempt
                st.error(f"Failed to send email to {recipient_email} after {max_retries} attempts: Connection issue")
                return False
            st.warning(f"Connection issue, retrying... ({attempt + 1}/{max_retries})")
            time.sleep(2)  # Wait 2 seconds before retrying
        except Exception as e:
            st.error(f"Failed to send email to {recipient_email}: {str(e)}")
            return False

st.title("Geek Room Email Sender")

# File Upload
uploaded_file = st.file_uploader("Upload CSV file", type="csv")

if uploaded_file:
    data = pd.read_csv(uploaded_file)
    required_columns = {'First name', 'Email', 'Company Name'}
    
    # Check if required columns exist, regardless of additional columns
    if required_columns.issubset(data.columns):
        st.success(f"CSV file successfully uploaded and validated. Found columns: {', '.join(data.columns)}")
        st.dataframe(data.head())
    else:
        missing_columns = required_columns - set(data.columns)
        st.error(f"Missing required columns: {', '.join(missing_columns)}\nPlease ensure your CSV contains: {', '.join(required_columns)}")
        st.stop()

# SMTP Details
st.header("SMTP Configuration")
sender_email = st.text_input("Your Email")
sender_password = st.text_input("Your Email Password", type="password")
smtp_server = st.text_input("SMTP Server", value="smtp.gmail.com")
smtp_port = st.number_input("SMTP Port", value=587)

# Email Subject and Message
st.header("Email Content")
subject = st.text_input("Email Subject", value="Exciting Opportunities in Machine Learning and LLMs")

default_template = (
    "Hi {First name},\n\n"
    "I hope this message finds you well. I am writing to express my strong interest in roles related to "
    "Machine Learning and Large Language Models (LLM) within your esteemed organization.\n\n"
    "With a background in Computer Science and hands-on experience in AI research, I have a proven track "
    "record in fine-tuning large language models and developing innovative AI solutions. My role as Co-founder "
    "of Geek Room and internships at Superteams.ai, Quizzy, and Renix Informatics have honed my skills in "
    "machine learning, leadership, and project management.\n\n"
    "I am particularly excited about contributing to your initiatives in improving recommendation systems, "
    "search algorithms, and natural language understanding. My projects, such as Dockerized-Whisper and Advocate Falcon, "
    "along with specialized coursework in Supervised Machine Learning and Transformers.\n\n"
    "I'm mentioning my proof of work with you:\n\n"
    "My HuggingFace Spaces: https://huggingface.co/themanas021\n"
    "My Github: https://github.com/manas95826\n"
    "My Linkedin: https://www.linkedin.com/in/themanas95826/\n"
    "My docker container: Manas - https://hub.docker.com/u/themanas\n"
    "My Resume: https://drive.google.com/file/d/1v51ZCWmIwWXdyZer81Y9s8KANUouT6us/view?usp=drivesdk\n\n"
    "Thank you for considering my application. I look forward to the opportunity to discuss how my background "
    "aligns with your team’s needs.\n\n"
    "Best regards,\n\n"
    "Manas Chopra\n"
    "8929891510"
)

# Store the edited message in message_template
message_template = st.text_area("Email Message Template", value=default_template, height=300)

# Sending Emails
if st.button("Send Emails"):
    if not sender_email or not sender_password:
        st.error("Please provide your email and password.")
    else:
        progress_bar = st.progress(0)
        total_emails = len(data)
        
        for index, row in data.iterrows():
            personalized_message = message_template.format(**row)
            if send_email(
                smtp_server, smtp_port, sender_email, sender_password,
                row['Email'], subject, personalized_message
            ):
                st.success(f"Email sent to {row['First name']} at {row['Email']}")
            else:
                st.error(f"Failed to send email to {row['First name']} at {row['Email']}.")
            
            # Update progress bar
            progress_bar.progress((index + 1) / total_emails)
            
            # Add a small delay between emails to prevent rate limiting
            time.sleep(1)
