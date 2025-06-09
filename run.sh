#!/bin/bash

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Starting the application..."
python3 server.py 

echo "Starting webhook receiver server"
python3 webhook_receiver.py

echo "Application is running!"
echo " on server: http://0.0.0.0:8000"
