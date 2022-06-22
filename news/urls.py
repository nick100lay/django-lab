

from django.urls import include, path

from . import views


urlpatterns = [
    path("", views.main_page_view),
    path("news/<int:pk>", views.article_view),
    path("blogs", views.blogs_view),
    path("blogs/<int:pk>", views.blog_view),
    path("register/", views.register_view),
    path("login/", views.login_view),
    path("logout/", views.logout_view),
    path("edit_article/<int:pk>", views.edit_article_view),
    path("create_article/", views.create_article_view),
]
