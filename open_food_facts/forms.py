from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User


class LoginForm(forms.Form):
    username = forms.CharField(label="Pseudo", max_length=100)
    password = forms.CharField(label="Mot de passe", max_length=50, widget=forms.PasswordInput())


class UserForm(ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']
        labels = {
            'username': 'Pseudo', 'first_name': 'Prénom', 'last_name': 'Nom',
            'password': 'Mot de passe',
        }
