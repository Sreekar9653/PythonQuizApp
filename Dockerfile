FROM python:3.12

WORKDIR /QuizApp

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . /QuizApp

EXPOSE 8501

CMD ["streamlit", "run", "Python/streamfile.py", "--server.port=8501", "--server.address=0.0.0.0"]
