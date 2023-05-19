Install requirements.
```
pip install -r requirements.txt
```
Add .env file in the same folder as settings.py and database details and django secret key in .env file
```
SECRET_KEY=This_is_a_Demo_Secret_key
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp_host_name
EMAIL_HOST_USER=your_email
EMAIL_HOST_PASSWORD=your_password
EMAIL_PORT=Email_port
```

Make migrations ,migrate and then run the server
```
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```