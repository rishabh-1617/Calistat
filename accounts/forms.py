from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, AthleteProfile


class SignUpForm(UserCreationForm):
    """Section 6 -- registration fields: name, username, email, password."""
    full_name = forms.CharField(max_length=150)
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        full_name = self.cleaned_data["full_name"].split(" ", 1)
        user.first_name = full_name[0]
        user.last_name = full_name[1] if len(full_name) > 1 else ""
        if commit:
            user.save()
        return user


class OnboardingForm(forms.ModelForm):
    """Short, optional onboarding (section 6) -- experience + goal only."""
    class Meta:
        model = User
        fields = ["experience_level", "primary_goal"]


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = AthleteProfile
        fields = ["display_name", "bio", "avatar", "country"]
