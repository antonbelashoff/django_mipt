from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('accounts/login/', views.login_view, name='login'),
    path('accounts/register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('create_quiz/', views.create_quiz, name='create_quiz'),
    path('play/', views.play_quiz, name='play_quiz'),
    path('profile/', views.profile_view, name='profile'),
    path('add_question/<int:quiz_id>/<int:question_num>/', views.add_question, name='add_question'),
    path('add_choices/<int:question_id>/<int:question_num>/<int:choice_count>/', views.add_choices, name='add_choices'),
    path('take_quiz/<int:quiz_id>/', views.take_quiz, name='take_quiz'),
    path('delete_quiz/<int:quiz_id>/', views.delete_quiz, name='delete_quiz'),
    path('leaderboard/', views.leaderboard_view, name='leaderboard'),
]
