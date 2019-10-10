from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(label="Pseudo", max_length=100)
    password = forms.CharField(label="Mot de passe", max_length=50)
