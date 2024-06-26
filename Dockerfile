# start by pulling the python image
FROM python:3.11

# copy the requirements file into the image
COPY ./requirements.txt /fhe-api/requirements.txt 

# switch working directory
WORKDIR /fhe-api

# install the dependencies and packages in the requirements file
RUN pip install -r requirements.txt

# copy every content from the local file to the image
COPY ./*.py /fhe-api/

# UI
COPY static static

# Examples
COPY fhe_studio.circuits.json fhe_studio.circuits.json

# configure the container to run in an executed manner
ENTRYPOINT [ "python" ]

CMD ["app.py" ]