from django import forms
from django.contrib.auth.forms import UserCreationForm
from userauths.models import User
from django.core.exceptions import ValidationError

class UserRegisterForm(UserCreationForm):
	username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username', 'class': 'username-validation'}))
	email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email'}))
	password1 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Mot de passe'}))
	password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirmer le mot de passe'}))

	class Meta:
		model = User
		fields = ['username', 'email']

	def clean_username(self):
		username = self.cleaned_data['username']

		if ' ' in username:
			raise ValidationError("Le nom d'utilisateur ne doit pas contenir d'espaces.")

		if len(username) < 3 or len(username) > 12:
			raise ValidationError("Le nom d'utilisateur doit être entre 3 à 12 caracters.")
			
		return username
