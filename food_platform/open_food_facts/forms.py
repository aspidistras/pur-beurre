from django import forms


class UserForm(forms.Form):
    username = forms.CharField(label="Pseudo", max_length=100)
    name = forms.CharField(label="Nom", max_length=100)
    surname = forms.CharField(label="Prénom", max_length=100)
    email = forms.EmailField(label="Email", max_length=200)
    password = forms.CharField(label="Mot de passe", max_length=50)
