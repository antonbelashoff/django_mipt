from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    best_scores = models.JSONField(default=dict)

    def __str__(self):
        return f'{self.user.username} Profile'

    def update_best_score(self, quiz_id, score):
        quiz_id_str = str(quiz_id)
        if quiz_id_str not in self.best_scores or self.best_scores[quiz_id_str] < score:
            self.best_scores[quiz_id_str] = score
            self.save()


class Quiz(models.Model):
    title = models.CharField(max_length=255)
    short_description = models.CharField(max_length=255, blank=True)
    detailed_description = models.TextField(blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    question_count = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    average_rating = models.FloatField(default=0.0)
    average_score = models.FloatField(default=0.0)
    ratings_count = models.PositiveIntegerField(default=0)

    def update_average_rating(self, new_rating):
        self.ratings_count += 1
        self.average_rating = ((self.average_rating * (self.ratings_count - 1)) + new_rating) / self.ratings_count
        self.save()

    def update_average_score(self):
        all_profiles = Profile.objects.all()
        best_scores = [profile.best_scores[str(self.id)]
                       for profile in all_profiles if str(self.id) in profile.best_scores]
        if best_scores:
            self.average_score = sum(best_scores) / len(best_scores)
            self.save()

    def __str__(self):
        return self.title


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.CharField(max_length=255)

    def __str__(self):
        return self.text


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text
