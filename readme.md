Install Python

then install the requirements
pip install -r requirements.txt

To run the project,
enter the following command in the cmd
streamlit run Python/streamfile.py

This projects currently takes 1-3mins to generate the question.
First question takes more time due to less understanding.
Model can go slow for answers like "","\n"
Sometimes, model repeats the same question in different ways when user says, "I dont know" 

For evaluation, my model has around 10-15 question-answer pair along with the corresponding time taken by the user.
To summarize this, model takes around 4-6 minutes which is huge but can evaluate.

