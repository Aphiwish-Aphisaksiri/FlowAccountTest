# FlowAccountTest
This is a assessment for FlowAccount software engineer application

Python version 3.11.14

The required library are fastAPI and uvicorn
```
pip install fastapi uvicorn
```

To run the application, use the command below:
```
uvicorn main:app --reload
```
The application will be available at http://127.0.0.1:8000/docs

To use docker to run the application, use the commands below:
```
docker build -t flowaccounttest .
docker run --name fastapitest -p 8000:8000 flowaccounttest
```
Note: build the docker image only once, then you can run the container multiple times. Make sure to stop and remove the container before running a new one with the same name.

To remove the container after use, run:
```
docker rm fastapitest
```
Note: make sure the container is stopped before removing it.