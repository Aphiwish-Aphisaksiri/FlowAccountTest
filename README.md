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

To remove the container after use, run:
```
docker rm fastapitest
```