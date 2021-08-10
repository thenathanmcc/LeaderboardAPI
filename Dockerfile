FROM python:3.6

ADD . /leaderboard_api

WORKDIR /leaderboard_api

COPY requirements.txt ./

RUN pip3 install flask flask-cors gunicorn hvac

EXPOSE 8080
CMD ["gunicorn", "-b", "0.0.0.0:8080", "Leaderboard"]