FROM gcr.io/google_appengine/python
WORKDIR /app
RUN virtualenv /env
RUN pip install --upgrade pip
ENV VIRTUAL_ENV -p python3.5 /env
ENV PATH /env/bin:$PATH
COPY requirements.txt /app/
COPY . /app/
RUN pip install -r requirements.txt

RUN ["python", "-m", "init"]
RUN ["python", "-m", "Branch", "customers.json"]



