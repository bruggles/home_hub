#! /usr/bin/python3
from app_contents import app as application

if __name__ == "__main__":
    #import logging
    #logging.basicConfig(filename='error.log',level=logging.DEBUG)
    application.run(host='0.0.0.0',debug=True)

#application.run(host='0.0.0.0',debug=True)
