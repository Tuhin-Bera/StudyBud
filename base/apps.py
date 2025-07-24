from django.apps import AppConfig




## we are registering all the forms here 

class BaseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'base'
