from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


class SignUpForm(UserCreationForm):
    """Registration form.

    Django ships login and logout views but no signup view, so registration
    is the one auth piece we have to provide ourselves. This form handles the
    validation and password hashing; register_view() in views.py is what uses it.
    """

    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email')
