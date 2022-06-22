from django import forms
from django.contrib.auth.models import User
from . import models


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(
            label="Пароль",
            widget=forms.PasswordInput)
    password2 = forms.CharField(
            label="Повторите пароль",
            widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email")

    def clean_password2(self):
        data = self.cleaned_data
        if data["password"] != data["password2"]:
            raise forms.ValidationError("Пароль не совпадает")
        return data["password2"]


class UserLoginForm(forms.Form):
    username = forms.CharField(
            label="Имя пользователя")
    password = forms.CharField(
            label="Пароль",
            widget=forms.PasswordInput)


class ArticleEditForm(forms.ModelForm):
    class Meta:
        model = models.Article
        fields = ("title", "text", "image",)


class ArticleCreationForm(forms.ModelForm):
    class Meta:
        model = models.Article
        fields = ("title", "text", "blog", "image", "owner")
