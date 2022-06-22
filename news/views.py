from django.shortcuts import render, redirect
from django.http import HttpResponseNotFound, HttpResponseForbidden
from django.views.decorators.http import require_GET, require_http_methods
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import login, logout, authenticate

from . import models
from . import forms


def query_articles_to_show():
    return models.Article.objects\
            .prefetch_related("blog", "owner")


def serialize_blog(blog):
    return [blog.name, "/blogs/{}".format(blog.id)]


def serialize_user(user):
    return [user.first_name, user.last_name]


def serialize_article(article):
    return {
        "url": "/news/{}".format(article.id),
        "edit_url": "/edit_article/{}".format(article.id),
        "title": article.title,
        "blog": [
            serialize_blog(blog) for blog in article.blog.all()
        ],
        "owner": serialize_user(article.owner),
        "owner_id": article.owner_id,
        "image": article.image.url,
        "text": article.text,
        "published_date": article.published_date.strftime(
            "%d.%m.%y %H:%M"),
    }


@require_GET
def main_page_view(request):
    query = query_articles_to_show()\
            .order_by("-published_date")\
            [:5]
    articles = [serialize_article(article) for article in query]
    return render(request, "news/main_page.html", {
        "articles": articles,
    })

@require_GET
def article_view(request, pk):
    try:
        article = query_articles_to_show().get(pk=pk)
    except ObjectDoesNotExist:
        return HttpResponseNotFound("Такой новости не найдено")
    return render(request, "news/article_page.html", {
        "article": serialize_article(article),
    })


def query_blogs_to_show():
    return models.Blog.objects.order_by("name")


@require_GET
def blogs_view(request):
    query = query_blogs_to_show()
    blogs = [serialize_blog(blog) for blog in query]
    return render(request, "news/blogs.html", {
        "blogs": blogs,
    })


@require_GET
def blog_view(request, pk):
    try:
        blog = query_blogs_to_show().get(pk=pk)
    except ObjectDoesNotExist:
        return HttpResponseNotFound("Такого блога не существует")
    query = query_articles_to_show()\
            .filter(blog=pk)\
            .order_by("-published_date")
    articles = [serialize_article(article) for article in query]
    return render(request, "news/blog.html", {
        "blog": serialize_blog(blog),
        "articles": articles,
        "in_blog_articles_list": True,
    })



@require_http_methods(["POST", "GET"])
def register_view(request):
    if request.user.is_authenticated:
        return HttpResponseForbidden("Вы уже вошли")
    if request.method == "POST":
        user_form = forms.UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data["password"])
            new_user.save()
            login(request, new_user)
            return redirect("/")
    else:
        user_form = forms.UserRegistrationForm()
    return render(request, "register.html", {"user_form": user_form})


@require_http_methods(["POST", "GET"])
def login_view(request):
    if request.user.is_authenticated:
        return HttpResponseForbidden("Вы уже вошли")
    if request.method == "POST":
        user_form = forms.UserLoginForm(request.POST)
        if user_form.is_valid():
            username = user_form.cleaned_data["username"]
            password = user_form.cleaned_data["password"]
            user = authenticate(username=username,
                    password=password)
            if user is None:
                user_form.add_error(None, "Неверные имя пользователя или пароль.")
            else:
                login(request, user)
                return redirect("/")
    else:
        user_form = forms.UserLoginForm()
    return render(request, "login.html", {"user_form": user_form})


@require_http_methods(["POST", "GET"])
def logout_view(request):
    if not request.user.is_authenticated:
        return HttpResponseForbidden("Вы не вошли")
    logout(request)
    return redirect("/")


@require_http_methods(["POST", "GET"])
def edit_article_view(request, pk):
    try:
        article = models.Article.objects.get(pk=pk)
    except ObjectDoesNotExist:
        return HttpResponseNotFound("Такой новости не существует")
    redirect_url = "/news/{}".format(pk)
    if not request.user.is_authenticated:
        return HttpResponseForbidden("Вы не вошли, чтобы редактировать новость")
    if request.user.pk != article.owner_id:
        return HttpResponseForbidden("Это не ваша новость, чтобы ее редактировать")

    if request.method == "POST":
        edit_form = forms.ArticleEditForm(request.POST, request.FILES, instance=article)
        if edit_form.is_valid():
            edit_form.save()
            return redirect(redirect_url)
    else:
        edit_form = forms.ArticleEditForm(instance=article)
    return render(request, "news/article_edit_form.html", {
        "edit_form": edit_form,
        "cancel_url": redirect_url,
                })


@require_http_methods(["POST", "GET"])
def create_article_view(request):
    if not request.user.is_authenticated:
        return HttpResponseForbidden("Вы не вошли, чтобы создавать новость")
    if not request.user.is_superuser:
        return HttpResponseForbidden("Вы не админ, чтобы создавать новость")

    if request.method == "POST":
        creation_form = forms.ArticleCreationForm(request.POST, request.FILES)
        if creation_form.is_valid():
            creation_form.save()
            return redirect("/")
    else:
        creation_form = forms.ArticleCreationForm()
    return render(request, "news/article_creation_form.html", {
        "creation_form": creation_form,
        "is_creating_article": True,
                })
