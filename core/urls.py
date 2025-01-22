from django.urls import path
from .views import *

urlpatterns = [
    path("",home,name="home"),
    path("signup/",signUp,name="signup"),
    path("create_post/",create_post,name="createpost"),
    path("detail_post/<int:id>",detail_post,name="detailpost"),
    path("generate_blog/",generate_blog,name="generate_blog"),
]
