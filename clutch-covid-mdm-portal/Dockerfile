FROM python:3.7.7-slim-buster

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update

RUN apt-get update && \
    apt-get install -y software-properties-common && \
    rm -rf /var/lib/apt/lists/*

#RUN add-apt-repository universe
RUN sed -i "/^# deb.*universe/ s/^# //" /etc/apt/sources.list

RUN apt-get update

RUN apt-get -y install python-dev libsasl2-dev default-libmysqlclient-dev build-essential libpq-dev python3-dev gcc unixodbc-dev libffi-dev g++ libzbar-dev graphviz libgraphviz-dev pkg-config

RUN apt-get update \
        && apt-get install -y curl apt-transport-https gnupg2 \
        && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
        && curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list \
        && apt-get update \
        && ACCEPT_EULA=Y apt-get install -y msodbcsql17 mssql-tools

# install dependencies
RUN pip install --upgrade pip setuptools wheel

RUN pip install cython

RUN pip install uwsgi

COPY ./requirements.txt /usr/src/app/requirements.txt

RUN pip install -r requirements.txt

# copy project
COPY . /usr/src/app/

RUN mv /usr/src/app/rapid_test_crm_themes/dev/bootstrap.min.css /usr/local/lib/python3.7/site-packages/flask_appbuilder/static/appbuilder/css/bootstrap.min.css

RUN mv /usr/src/app/rapid_test_crm_themes/dev/bootstrap.min.css.map /usr/local/lib/python3.7/site-packages/flask_appbuilder/static/appbuilder/css/bootstrap.min.css.map

CMD ["python","run.py"]
#CMD ["uwsgi","app.ini"]
#COPY rapid_test_crm_themes/bootstrap.min.css /usr/local/lib/python3.7/site-packages/flask_appbuilder/static/appbuilder/css
