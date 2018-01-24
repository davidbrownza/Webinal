from django.conf.urls import patterns, url, include 
from main import views 
 
urlpatterns = patterns('main.views',

 	url(r'^users/login', 'sign_in'),
 	url(r'^users/logout', 'sign_out'),
	
 	url(r'^', 'index'),		
) 
