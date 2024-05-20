from django.shortcuts import (render,
                              redirect,
                              get_object_or_404)
from django.contrib import messages
from django.forms import inlineformset_factory
from django.contrib.auth import (login,
                                 authenticate,
                                 logout,
                                 update_session_auth_hash)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import (AuthenticationForm,
                                       UserCreationForm,
                                       PasswordChangeForm)
from .forms import (UserProfileForm,
                    ProfileForm,
                    QuizForm,
                    QuestionForm,
                    ChoiceForm)
from .models import (Profile,
                     Quiz,
                     Question,
                     Choice)


@login_required
def index(request):
    return render(request, 'home.html')


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def create_quiz(request):
    if request.method == 'POST':
        quiz_form = QuizForm(request.POST)
        if quiz_form.is_valid():
            quiz = quiz_form.save(commit=False)
            quiz.creator = request.user
            quiz.save()
            return redirect('add_question', quiz_id=quiz.id, question_num=1)
    else:
        quiz_form = QuizForm()
    return render(request, 'create_quiz.html', {'quiz_form': quiz_form})


@login_required
def add_question(request, quiz_id, question_num):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if request.method == 'POST':
        question_form = QuestionForm(request.POST)
        choice_count = int(request.POST.get('choice_count', 4))
        if question_form.is_valid():
            question = question_form.save(commit=False)
            question.quiz = quiz
            question.save()
            request.session['choice_count'] = choice_count
            return redirect('add_choices', question_id=question.id,
                            question_num=question_num, choice_count=choice_count)
    else:
        question_form = QuestionForm()
    return render(request, 'add_question.html',
                  {'quiz': quiz, 'question_form': question_form,
                   'question_num': question_num})


@login_required
def add_choices(request, question_id, question_num, choice_count):
    question = get_object_or_404(Question, id=question_id)
    quiz = question.quiz
    choice_form_set = inlineformset_factory(Question, Choice, form=ChoiceForm, extra=choice_count, can_delete=False)

    if request.method == 'POST':
        formset = choice_form_set(request.POST, instance=question)
        if formset.is_valid():
            correct_choices = sum([form.cleaned_data.get('is_correct', False) for form in formset])
            if correct_choices != 1:
                formset.non_form_errors = ["Должен быть выбран только один правильный ответ."]
            else:
                formset.save()
                if question_num < quiz.question_count:
                    return redirect('add_question', quiz_id=quiz.id, question_num=question_num + 1)
                else:
                    return redirect('home')
    else:
        formset = choice_form_set(instance=question)

    return render(request, 'add_choices.html', {
        'question': question,
        'formset': formset,
        'question_num': question_num,
    })


@login_required
def profile_view(request):
    if not hasattr(request.user, 'profile'):
        Profile.objects.create(user=request.user)

    user_form = UserProfileForm(instance=request.user)
    profile_form = ProfileForm(instance=request.user.profile)
    password_form = PasswordChangeForm(request.user)
    form_with_errors = None

    if request.method == 'POST':
        if 'username' in request.POST:
            user_form = UserProfileForm(request.POST, instance=request.user)
            if user_form.is_valid():
                user_form.save()
                return redirect('profile')
            else:
                form_with_errors = 'user_form'
        elif 'first_name' in request.POST:
            profile_form = ProfileForm(request.POST, instance=request.user.profile)
            if profile_form.is_valid():
                profile_form.save()
                return redirect('profile')
            else:
                form_with_errors = 'profile_form'
        elif 'old_password' in request.POST:
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                return redirect('profile')
            else:
                form_with_errors = 'password_form'

    best_scores = request.user.profile.best_scores
    quizzes = Quiz.objects.filter(id__in=best_scores.keys())
    quiz_scores = [(quiz.title, best_scores[str(quiz.id)]) for quiz in quizzes]

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'password_form': password_form,
        'form_with_errors': form_with_errors,
        'quiz_scores': quiz_scores,
    }
    return render(request, 'profile.html', context)


@login_required
def play_quiz(request):
    quizzes = Quiz.objects.all()
    context = {
        'quizzes': quizzes,
    }
    return render(request, 'play_quiz.html', context)


@login_required
def take_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.questions.all()
    results = []
    score = 0
    # rating_given = False

    if request.method == 'POST':
        for question in questions:
            selected_choice_id = request.POST.get(f'question_{question.id}')
            if selected_choice_id:
                selected_choice = Choice.objects.get(id=selected_choice_id)
                if selected_choice.is_correct:
                    score += 1
                    results.append((question, True))
                else:
                    results.append((question, False))
            else:
                results.append((question, False))

        if 'rating' in request.POST:
            rating = int(request.POST['rating'])
            quiz.update_average_rating(rating)

        request.user.profile.update_best_score(quiz_id, score)
        quiz.update_average_score()

        context = {
            'quiz': quiz,
            'score': score,
            'total': len(questions),
            'results': results,
            'rating_given': 'rating' in request.POST
        }
        return render(request, 'quiz_result.html', context)

    context = {
        'quiz': quiz,
        'questions': questions
    }
    return render(request, 'take_quiz.html', context)


@login_required
def delete_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, creator=request.user)
    if request.method == 'POST':
        quiz.delete()
        messages.success(request, 'Викторина успешно удалена.')
        return redirect('play_quiz')
    return redirect('play_quiz')


@login_required
def leaderboard_view(request):
    quizzes = Quiz.objects.all()
    leaderboard_data = []

    for quiz in quizzes:
        profiles = Profile.objects.all()
        scores = [(profile.user.username, profile.best_scores.get(str(quiz.id), 0)) for profile in profiles]
        scores.sort(key=lambda x: x[1], reverse=True)
        leaderboard_data.append({
            'quiz': quiz,
            'scores': scores
        })

    context = {
        'leaderboard_data': leaderboard_data
    }
    return render(request, 'leaderboard.html', context)
