*Note: this service is not secure or ready to be used yet. Installation instructions may not work.*

# Webinal
Web-based code editor and terminal. 

### Getting started:

* Install pip and virtualenv (if not already installed):
```
https://bootstrap.pypa.io/get-pip.py
sudo python get-pip.py
pip install virtualenv
```

* Download Webinal:
```
git clone https://github.com/Stavatech/Webinal.git
cd Webinal
```

* Set up virtual environment and install dependencies:
```
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

* Set location of `IMPERSONATOR_KEY` in `Webinal/settings.py`

* Update hardcoded paths in `impersonator/server.py`

* Start the Impersonator service:
```
cd impersonator
sudo start.sh
cd ../
```

* Create the DB:
```
./manage.py syncdb
```

* Run Webinal:
```
./manage.py runserver 
