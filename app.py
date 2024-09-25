import streamlit as st
from code_editor import code_editor
import bcrypt
import pandas as pd
import uuid
from datetime import datetime

# Function to hash passwords
def HashPasswd(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

# Function to check password hash
def CheckPasswdHash(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

# Streamlit app
tab1, tab2 = st.tabs(['Download', 'Upload'])

code = """
# Hit Control Enter after done Coding for next steps
print('Hello World!!') 
"""

# Download Tab
with tab1:
    name = st.text_input('Enter Name', key = '1')
    passd = st.text_input('Password', key = '2', type='password')
    
    if st.button('Submit'):
        data = pd.read_json('data.json')
        user_files = []
        
        for entry in data.to_dict(orient='records'):
            if entry['name'] == name and CheckPasswdHash(passd, entry['passwd']):
                user_files = entry['files']
        
        if not user_files:
            st.error('Username or Password are Incorrect or No Files Found')
        else:
            st.success('Login successful!')
            st.write("Your files:")
            for file in user_files:
                st.write(f"Date: {file['date']}, Tag: {file['tag']}")
                with open(file['name'], 'r') as f:  # Open as text file
                    st.download_button(label='Download',
                                       data=f,
                                       file_name='_'.join(file['tag'].split()) + '.' + (file['name'].split('.'))[1],
                                       mime='text/plain')  # Specify MIME type for text files

# Upload Tab
# Upload Tab
with tab2:
    name = st.text_input('Enter Name', key='3')
    passd = st.text_input('Password', key='4', type='password')
    tag = st.text_input('File Tag', key='5')
    
    # Load existing data or create a new DataFrame if the file does not exist
    try:
        data = pd.read_json('data.json')
    except (ValueError, FileNotFoundError):
        data = pd.DataFrame(columns=['name', 'passwd', 'files'])  # Create empty DataFrame with defined columns

    response_dict = code_editor(code)

    if response_dict['text'] != '':
        fileext = st.text_input('Enter file Extension', '.py')  # Default extension
        if st.button('Save'):
            file_name = f"{uuid.uuid4()}{fileext}"
            with open(file_name, 'w') as file:
                file.write(response_dict['text'])
            
            zap = False
            for entry in data.to_dict(orient='records'):
                if entry['name'] == name and CheckPasswdHash(passd, entry['passwd']):
                    entry['files'].append({'name': file_name, 'date': str(datetime.now()), 'tag': tag})
                    zap = True
            
            if not zap:
                new_data = {
                    'name': name,
                    'passwd': HashPasswd(passd),
                    'files': [{'name': file_name, 'date': str(datetime.now()), 'tag': tag}]
                }
                
                # Convert the new data to a DataFrame
                new_data_df = pd.DataFrame([new_data])
                
                # Use pd.concat to append the new DataFrame
                data = pd.concat([data, new_data_df], ignore_index=True)
            
            # Save updated DataFrame back to JSON
            data.to_json('data.json', orient='records', lines=False)  # Save as JSON
