"""forms creating module"""

from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User


class LoginForm(forms.Form):
    """defines the login form's fields"""

    username = forms.CharField(label="Pseudo", max_length=100)
    password = forms.CharField(label="Mot de passe", max_length=50, widget=forms.PasswordInput())


class UserForm(ModelForm):
    """defines the user creating form's fields"""

    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        """alters django's original UserForm class"""

        model = User
        # defines which fields are to be displayed
        fields = ['username', 'first_name', 'last_name', 'email', 'password']
        # defines the labels displayed
        labels = {
            'username': 'Pseudo', 'first_name': 'Prénom', 'last_name': 'Nom',
            'password': 'Mot de passe',
        }

        help_texts = {
            'username': None,
        }

