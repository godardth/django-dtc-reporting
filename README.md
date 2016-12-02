INSTALLATION  
  
virtualenv venv  
source venv/bin/activate  
pip install -r requirements.txt  
npm install -g bower  
./manage.py bower install  
./manage.py migrate  
./manage.py createsuperuser  
./manage.py runserver 0.0.0.0:8080  