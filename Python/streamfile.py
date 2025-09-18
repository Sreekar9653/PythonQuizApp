import streamlit as st                      # For using streamlit
import streamlit.components.v1 as components
import time                                 # to implement sleep
import pandas as pd                         # For dealing with dataframes
import base64                               # to convert images to base 64
import re
import utils
import os                                   # To get operating system information
import json

hr_image=os.getcwd()+"/"+'images/hr.jpg'
user_image=os.getcwd()+"/"+'images/user.png'
icon=os.getcwd()+"/"+'images/Servletlogo.png'
st.set_page_config(page_title="SreeQuizApp",page_icon=icon)

# ------------- Caching icons ------------------
@st.cache_data                                      
def get_img_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# ------------ Initializing Session variables --------------
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if 'continue_timer' not in st.session_state:
    st.session_state.continue_timer=1
    st.session_state.curtime=0
    st.session_state.spent_time=0
if 'show_dialog' not in st.session_state:
    st.session_state.show_dialog=True
if 'time_taken' not in st.session_state:
    st.session_state.time_taken=[]
if 'user_cur_state' not in st.session_state:
    st.session_state.user_cur_state='login'
if "test_start_time" not in st.session_state:
    st.session_state.test_start_time = 0
    st.session_state.test_rem_time = 0
if 'teststatus' not in st.session_state:
    st.session_state.teststatus='Loading your Exam Page...'
if "user" not in st.session_state:
    st.session_state.username = ""
    st.session_state.usertype = ""
    st.session_state.user = ""
if "userloginmsg" not in st.session_state:
    st.session_state.userloginmsg = ""


# ------------- Check login ----------------
users=utils.getusers()

with st.sidebar:
    if(not st.session_state.user):
        login,signup = st.tabs(["Login","Signup"])
        with login:
            username = st.text_input("Username",key="luser")
            password= st.text_input("Password",type="password",key="lpass")
            submit = st.button("Login",key="lsubmit")
            if submit and username and password:
                if not users.get(username,dict({})):
                    warning=st.warning(f"User {username} not found")
                    print(username,password,sep=" - ")
                    time.sleep(2)
                    warning.empty()
                elif(utils.checkuser(password,username)):
                    st.session_state.username = username
                    st.session_state.user=users[username]["name"]
                    st.session_state.usertype=users[username]["usertype"]
                    st.session_state.userloginmsg="Login successful"
                    st.rerun()
                else:
                    warning=st.warning("Invalid Credentials")
                    print(username,password,sep=" - ")
                    time.sleep(2)
                    warning.empty()

        with signup:
            name = st.text_input("Name",key="sname")
            username = st.text_input("Preffered Username",key="suser")
            password= st.text_input("Password",type="password",key="spass")
            submit = st.button("Signup",key="ssubmit")
            if submit and username and password and name:
                if username in users:
                    warning=st.warning("Username already exists")
                    time.sleep(2)
                    warning.empty()
                else:
                    utils.adduser(name,username,password)
                    st.session_state.username = username
                    st.session_state.usertype=users[username]["usertype"]
                    st.session_state.user=name
                    st.session_state.userloginmsg="New user created"
                    st.rerun()
    else:
        if(st.session_state.userloginmsg):
            logininfomsg=st.info(st.session_state.userloginmsg)
            time.sleep(1)
            logininfomsg.empty()
            st.session_state.userloginmsg=""
        st.caption(f"<p align='right' style='font-size:30px'>Hello {st.session_state.user}!</p>",unsafe_allow_html=True)
        if st.button("Logout"):
            st.toast("User logged out successfully")
            st.session_state.user=""
            st.session_state.username = ""
            st.session_state.user_cur_state='login'
            st.session_state.messages = []
            st.session_state.continue_timer=1
            st.session_state.curtime=0
            st.session_state.spent_time=0
            st.session_state.time_taken=[]
            st.session_state.test_start_time = 0
            st.session_state.test_rem_time = 0
            st.session_state.show_dialog=True
            st.session_state.teststatus='Loading your Exam Page...'
            st.session_state.userloginmsg = ""
            st.rerun()
    
# ------------- Fragments ----------------
@st.fragment(run_every=1)
def starttimer(countdown,statevalue="",change_state=True):
    try:
        timedif=int(countdown-time.time()+st.session_state.curtime) if(st.session_state.continue_timer) else timedif
        timetext=st.markdown(f"""
            <div style='border:4px black ridge;padding:5px;border-radius:5px;text-align:right;width:fit-content;float:right'>
                Time left: {timedif / 60:02d}min : {timedif % 60:02d}sec
            </div>""",unsafe_allow_html=True)
        
        if(not change_state):st.session_state.test_rem_time-=1
        if(timedif<=0):
            st.session_state.continue_timer=0
            timetext.empty()
            if(change_state):
                st.session_state.show_dialog=False
                st.session_state.user_cur_state=statevalue
                if(st.session_state.test_rem_time!=0):
                    st.session_state.test_rem_time=30*60 - (time.time()-st.session_state.test_start_time)
                else:
                    st.session_state.test_rem_time=30*60
                    st.session_state.test_start_time=time.time()
            
            elif st.session_state.test_rem_time<=0:
                st.session_state.user_cur_state="End"
            st.rerun()
    except Exception as e:pass

def close_dialog():
    hide_button_style = """
        <style>
        div[aria-label="dialog"]{
            display: none !important;
        }
        </style>
    """
    st.markdown(hide_button_style, unsafe_allow_html=True)

if not st.session_state.show_dialog:
    close_dialog()

@st.dialog("Need more time to read?",width="large")
def end_inst_dialog():
    st.markdown("**Please note**: You **cannot** see instructions later")
    if st.button("Yes, I want to read"):
        st.session_state.continue_timer=1
        st.session_state.spent_time=time.time()-st.session_state.curtime
        st.rerun()
    if st.button("No"):
        st.session_state.user_cur_state='test'
        st.session_state.show_dialog=False
        if(st.session_state.test_rem_time!=0):
            st.session_state.test_rem_time=30*60 - (time.time()-st.session_state.test_start_time)
        else:
            st.session_state.test_rem_time=30*60
            st.session_state.test_start_time=time.time()
        st.rerun()

def answerfunc():
    answer=st.session_state["answer"+str(num_questions)]
    st.session_state.messages[-1][1] = answer
    st.session_state.time_taken[-1] = int(time.time()-que_start_time)

# After login condition
if(st.session_state.user and st.session_state.usertype=='candidate'):
    # ------------ Homepage --------------------
    if st.session_state.user_cur_state=='login':
        remsecs=300 - st.session_state.spent_time
        st.session_state.curtime=time.time()
        starttimer(remsecs,'test')
        instructions=open("html/instructions.html",encoding="utf-8").read()
        st.markdown(instructions,unsafe_allow_html=True)
        if(st.button("I am ready to start")):
            st.session_state.continue_timer=0
            end_inst_dialog()
            hide_button_style = """
                <style>
                button[aria-label="Close"] {
                    display: none !important;
                }
                </style>
            """
            st.markdown(hide_button_style, unsafe_allow_html=True)

    elif st.session_state.user_cur_state=='test':
        intro=st.columns([0.1,0.8],vertical_alignment='center')
        with intro[0]:
            st.image(hr_image)
        with intro[1]:
            st.text("Hi, I am Sree, I'm your technical HR for this interview")
        # st.chat_message("Interviewer", avatar=hr_image).write(start_msg)
        st.divider()
        num_questions=0
        if st.session_state.messages:
            for question,answer in st.session_state.messages:
                st.chat_message("Interviewer", avatar=hr_image).text(f"{num_questions+1}. {question}")
                st.chat_message("Candidate", avatar=user_image).text(answer)
                num_questions+=1
                st.divider()

        if(st.session_state.test_rem_time<=0):
            st.session_state.user_cur_state='End'
            st.rerun()
        with st.spinner("Thinking.."):
            question=utils.findquestions(st.session_state.messages)
            question=question.replace('"','').strip()
        
        if(not question):
            st.text(question)
            st.stop()

        que_start_time=time.time()
        starttimer(120,change_state=False)
        st.session_state.curtime=time.time()
        st.session_state.continue_timer=1
        st.session_state.messages.append([question, ""])
        st.session_state.time_taken.append(0)
        st.chat_message("Interviewer", avatar=hr_image).write(f"{num_questions+1}. {question}")
        answer = st.chat_input("Enter your answer",key="answer"+str(num_questions),on_submit=answerfunc)

    elif st.session_state.user_cur_state=='End':   
        st.text("Your test answers are being saved. Please wait for a moment.../nPlease Dont close the window")
        with st.spinner("Saving your answers..."):
            print(utils.evaluate(st.session_state.username,st.session_state.messages,st.session_state.time_taken))
            st.session_state.user_cur_state='Completed'
            st.rerun()
    
    elif st.session_state.user_cur_state=='Completed':
        successmsg=st.success("Your answers are saved successfully")
        st.text("Your Answers have been saved./nThank you for your patience./nNow you can close the window./n/n")
        st.markdown("<big><b>Note</b> : Once submitted, you <b>cannot reappear</b> for the test again.</big>",unsafe_allow_html=True)
        time.sleep(2)
        successmsg.empty()

elif(st.session_state.user and st.session_state.usertype.lower()=='hr'):
    st.title("HR Dashboard")
    st.markdown("You can view the test results of candidates here.")
    df1,df2=utils.getresults()
    data_page=st.tabs(["Users Data","Tests Data"])
    if data_page=="Users Data":
        if len(df1)==0:
            st.info("No user data found.")
        else:
            st.dataframe(df1)
            csv = df1.to_csv().encode('utf-8')
            st.download_button(
                label="Download data as CSV",
                data=csv,
                file_name='test_results.csv',
                mime='text/csv',
            )
    else:
        if len(df2)==0:
            st.info("No test data found.")
        else:
            st.dataframe(df2)
            csv = df2.to_csv().encode('utf-8')
            st.download_button(
                label="Download data as CSV",
                data=csv,
                file_name='test_results.csv',
                mime='text/csv',
            )

else:
    imgheader=get_img_as_base64(os.getcwd()+"/"+"images/Servletlogo.png")
    htmltext = f"""
    <div>
        <br>
        <div style='border:1px #00000055 solid;border-radius:15px;background-color:#D6D2C599;'>
        <br>
        <img src="data:image/png;base64,{imgheader}" style="display: block; margin-left: auto; margin-right: auto;"><br>
        </div><br>
        <div style='display:flex;color:black;justify-content:center;align-items:center,letter-spacing:1.5'>
        <ol>
        <li>Please login/signup to continue</li>
        <li>Read the instructions carefully and start the test.</li>
        <li>Allow camera and mic permissions when prompted</li>
        <li>Your interview questions and answers will be in chatting format.</li>
        </ol>
        </div>
    </div>
    """

    st.markdown(htmltext,unsafe_allow_html=True)


