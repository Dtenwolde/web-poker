# Web-poker

To setup the server, configure a python interpreter first.
Create an environment using the following command;

    python -m pip install virtualenv
    virtualenv -p python venv
    
Then, activate the environment;

For linux

    ./venv/bin/activate
    
For windows
   
    call .\venv\Scripts\activate.bat
    
Install all required packages to run the server 

    python -m pip install -r requirements.txt
    
Then you can run the server

    python run.py