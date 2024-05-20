from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm
from .models import Profile, Quiz, Question, Choice


class UserProfileForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        labels = {
            'username': 'Имя пользователя',
            'email': 'Электронная почта',
            'password': 'Пароль'
        }


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('first_name', 'last_name')
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия'
        }


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'short_description', 'detailed_description', 'question_count']
        labels = {
            'title': 'Название',
            'short_description': 'Краткое описание',
            'detailed_description': 'Подробное описание',
            'question_count': 'Количество вопросов'
        }


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text']
        labels = {
            'text': 'Текст вопроса'
        }


class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['text', 'is_correct']
        labels = {
            'text': 'Текст варианта ответа',
            'is_correct': 'Правильный ответ'
        }
