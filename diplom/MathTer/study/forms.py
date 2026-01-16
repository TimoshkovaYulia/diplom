from django import forms
from .models import Course, User
from django.contrib.auth.forms import AuthenticationForm


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'grade_level']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'input-field'}),
            'description': forms.Textarea(attrs={'class': 'input-field'}),
            'grade_level': forms.Select(attrs={'class': 'input-field'}),
        }

class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput
    )
    password2 = forms.CharField(
        label="Повторите пароль",
        widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ["username", "role"]

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("password1") != cleaned_data.get("password2"):
            raise forms.ValidationError("Пароли не совпадают")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Имя пользователя")
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput
    )