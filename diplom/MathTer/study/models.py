from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver



class User(AbstractUser):
    ROLE_CHOICES = [
        ('student', 'Ученик'),
        ('teacher', 'Учитель'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_premium = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    
    groups = models.ManyToManyField(
        Group,
        related_name='study_users',
        blank=True,
        help_text='The groups this user belongs to.'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='study_users_permissions',
        blank=True,
        help_text='Specific permissions for this user.'
    )

    def anonymize(self):
        username_to_save = self.username

        if hasattr(self, 'student_profile') and self.student_profile:
            student = self.student_profile
            for attempt in student.task_attempts.all():
                attempt.deleted_student_name = username_to_save
                attempt.save()
            for result in student.homework_results.all():
                result.deleted_student_name = username_to_save
                result.save()
            for rec in student.recommendations.all():
                rec.deleted_student_name = username_to_save
                rec.save()
            for progress in student.progress.all():
                progress.deleted_student_name = username_to_save
                progress.save()
            for group_link in student.group_memberships.all():
                group_link.deleted_student_name = username_to_save
                group_link.save()
            for dialog in student.ai_dialogs.all():
                dialog.student = None
                dialog.save()
            for session in student.free_chat_sessions.all():
                session.student = None
                session.save()

        self.username = f"deleted_{self.id}"
        self.email = None
        self.password = None
        self.is_active = False
        self.save()

    def __str__(self):
        return self.username



class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class Student(models.Model):
    GRADE_LEVEL_CHOICES = [
        ('5-9', '5-9 класс'),
        ('10-11', '10-11 класс'),
        ('student', 'Студент'),
        ('older', 'Старше'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    deleted_student_name = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    grade_level = models.CharField(max_length=20, choices=GRADE_LEVEL_CHOICES, default='5-9')
    current_level = models.PositiveIntegerField(default=1)
    learning_style = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.user.username if self.user else self.deleted_student_name


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == 'student':
            Student.objects.create(user=instance, grade_level='5-9')
        elif instance.role == 'teacher':
            Teacher.objects.create(user=instance)



class Course(models.Model):
    GRADE_LEVEL_CHOICES = [(i, f"{i} класс") for i in range(5, 12)]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    grade_level = models.PositiveIntegerField(choices=GRADE_LEVEL_CHOICES, default=5)


    def __str__(self):
        return self.title


class Topic(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='topics')
    title = models.CharField(max_length=255)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_courses') 

    def __str__(self):
        return f"{self.course.title} - {self.title}"



class Task(models.Model):
    DIFFICULTY_CHOICES = [
        (1, 'Лёгкий'),
        (2, 'Средний'),
        (3, 'Сложный'),
    ]
    TASK_TYPE_CHOICES = [
        ('test', 'Тест'),
        ('open_answer', 'Открытый ответ'),
        ('solution', 'Решение с объяснением'),
    ]

    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    task_type = models.CharField(max_length=30, choices=TASK_TYPE_CHOICES)
    difficulty = models.PositiveSmallIntegerField(choices=DIFFICULTY_CHOICES, default=1)
    max_score = models.PositiveIntegerField(default=10)
    content = models.JSONField()

    def __str__(self):
        return f"{self.topic.title} - {self.title}"


class TaskAttempt(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='attempts')
    student = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='task_attempts')
    deleted_student_name = models.CharField(max_length=255, null=True, blank=True)
    answer = models.TextField()
    is_correct = models.BooleanField(null=True)
    score = models.PositiveIntegerField(default=0)
    ai_feedback = models.TextField(blank=True)
    completed_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.student is None and not self.deleted_student_name:
            self.deleted_student_name = "Deleted Student"
        super().save(*args, **kwargs)


class StudentProgress(models.Model):
    student = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='progress')
    deleted_student_name = models.CharField(max_length=255, null=True, blank=True)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='student_progress')
    completion_rate = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)], default=0.0)
    average_score = models.FloatField(default=0.0)
    last_activity = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.student is None and not self.deleted_student_name:
            self.deleted_student_name = "Deleted Student"
        super().save(*args, **kwargs)



class StudyGroup(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_groups')
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class GroupStudent(models.Model):
    group = models.ForeignKey(StudyGroup, on_delete=models.CASCADE, related_name='students')
    student = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='group_memberships')
    deleted_student_name = models.CharField(max_length=255, null=True, blank=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('group', 'student')

    def save(self, *args, **kwargs):
        if self.student is None and not self.deleted_student_name:
            self.deleted_student_name = "Deleted Student"
        super().save(*args, **kwargs)



class Homework(models.Model):
    group = models.ForeignKey(StudyGroup, on_delete=models.CASCADE, related_name='homeworks')
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='homeworks')
    tasks = models.ManyToManyField(Task, related_name='homeworks')  # <-- добавляем существующие задачи
    due_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Homework for {self.group.name} on {self.topic.title}"


class HomeworkResult(models.Model):
    homework = models.ForeignKey(Homework, on_delete=models.CASCADE, related_name='results')
    student = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='homework_results')
    total_score = models.PositiveIntegerField(default=0)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"HomeworkResult for {self.student.username if self.student else 'Deleted Student'}"



class AiDialog(models.Model):
    student = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='ai_dialogs')
    task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True, blank=True)
    user_message = models.TextField()
    ai_response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class AiFreeChatSession(models.Model):
    student = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='free_chat_sessions')
    started_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Free chat session for {self.student.username} started at {self.started_at}"


class AiFreeChatMessage(models.Model):
    session = models.ForeignKey(AiFreeChatSession, on_delete=models.CASCADE, related_name='messages')
    sender = models.CharField(max_length=20)  # "student" или "ai"
    message_text = models.TextField()
    error_type = models.CharField(max_length=50, null=True, blank=True)
    error_description = models.TextField(null=True, blank=True)
    confidence_score = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} at {self.created_at}: {self.message_text[:30]}"


class AiRecommendation(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recommendations')
    recommended_topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, blank=True)
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Recommendation for {self.student.username}: {self.recommended_topic.title if self.recommended_topic else 'None'}"
