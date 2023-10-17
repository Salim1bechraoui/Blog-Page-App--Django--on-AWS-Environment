
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'database1',  # database name in RDS is written here
        'USER': 'admin',  # database master username in RDS is written here
        'PASSWORD': config('PASSWORD'),
        # database endpoint is written here
        'HOST': 'aws-capstone-rds.cukd79ofsohr.us-east-1.rds.amazonaws.com',
        'PORT': '3306'  # database port number is written here
    }
}