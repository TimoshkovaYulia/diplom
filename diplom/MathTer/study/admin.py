from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, Student, Teacher, StudyGroup, GroupStudent

# -----------------------
# Форма для создания пользователя
# -----------------------
class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'role')  # Только нужные поля


# -----------------------
# Форма для изменения пользователя
# -----------------------
class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'role', 'is_premium', 'is_active')


# -----------------------
# Inline форма для студента
# -----------------------
class StudentInline(admin.StackedInline):
    model = Student
    can_delete = False
    verbose_name_plural = 'Student Profile'
    fk_name = 'user'

    # Поля, которые нельзя редактировать (автоматические)
    readonly_fields = ('deleted_student_name', 'current_level', 'learning_style')

    # Показываем только редактируемые поля
    fields = ('grade_level',)


# -----------------------
# Inline форма для учителя
# -----------------------
class TeacherInline(admin.StackedInline):
    model = Teacher
    can_delete = False
    verbose_name_plural = 'Teacher Profile'
    fk_name = 'user'


# -----------------------
# Кастомный UserAdmin
# -----------------------
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    # Поля, которые отображаются при редактировании
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password', 'role', 'is_premium')}),
        ('Important dates', {'fields': ('last_login', 'created_at')}),  # readonly_fields ниже
    )

    # Поля для формы создания пользователя
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role')
        }),
    )

    # Поля, которые нельзя редактировать
    readonly_fields = ('created_at', 'last_login')

    list_display = ('username', 'email', 'role', 'is_premium', 'is_active', 'last_login', 'created_at')
    list_filter = ('role', 'is_premium', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('username',)

    filter_horizontal = ()  # убираем встроенные M2M поля Django (groups, permissions)

    # Динамически показываем inline форму в зависимости от роли
    def get_inline_instances(self, request, obj=None):
        inlines = []
        if obj:
            if obj.role == 'student':
                inlines = [StudentInline(self.model, self.admin_site)]
            elif obj.role == 'teacher':
                inlines = [TeacherInline(self.model, self.admin_site)]
        return inlines

from django.contrib import admin
from .models import (
    Student, Teacher, Course, Topic, Task, TaskAttempt,
    StudentProgress, StudyGroup, GroupStudent, Homework, HomeworkResult
)

# -----------------------
# Student admin
# -----------------------
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'grade_level', 'created_at')
    search_fields = ('user__username', 'user__email')
    fields = ('user', 'grade_level')  # показываем только редактируемые при создании
    readonly_fields = ('deleted_student_name', 'current_level', 'learning_style', 'created_at')


# -----------------------
# Teacher admin
# -----------------------
@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    search_fields = ('user__username', 'user__email')
    fields = ('user',)  # на этапе создания
    readonly_fields = ('created_at',)


# -----------------------
# Course admin
# -----------------------
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'grade_level', )
    search_fields = ('title',)
    fields = ('title', 'description', 'grade_level', )


# -----------------------
# Topic admin
# -----------------------
@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'course',)
    search_fields = ('title',)
    fields = ('course', 'title',)


# -----------------------
# Task admin
# -----------------------
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'topic', 'task_type', 'difficulty', 'max_score')
    search_fields = ('title',)
    fields = ('topic', 'title', 'description', 'task_type', 'difficulty', 'max_score', 'content')


# -----------------------
# TaskAttempt admin
# -----------------------
@admin.register(TaskAttempt)
class TaskAttemptAdmin(admin.ModelAdmin):
    list_display = ('task', 'student', 'score', 'completed_at')
    search_fields = ('student__username',)
    fields = ('task', 'student', 'answer')  # выводим только при создании
    readonly_fields = ('is_correct', 'score', 'ai_feedback', 'completed_at', 'deleted_student_name')


# -----------------------
# StudentProgress admin
# -----------------------
@admin.register(StudentProgress)
class StudentProgressAdmin(admin.ModelAdmin):
    list_display = ('student', 'topic', 'average_score', 'completion_rate', 'last_activity')
    search_fields = ('student__username',)
    fields = ('student', 'topic')  # редактируем только связь при создании
    readonly_fields = ('average_score', 'completion_rate', 'last_activity', 'deleted_student_name')


class GroupStudentInline(admin.TabularInline):
    model = GroupStudent
    extra = 1  # сколько пустых форм показывать сразу
    # autocomplete_fields = ['student']  # удобный поиск по имени
    can_delete = False
    fields = ['student']

    # Показываем только учеников
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'student':
            kwargs['queryset'] = User.objects.filter(role='student').order_by('username')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(StudyGroup)
class StudyGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'teacher')
    # readonly_fields = ('created_at',)
    inlines = [GroupStudentInline]  # добавляем учеников прямо на странице группы

    # Показываем только учителей при выборе teacher
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'teacher':
            kwargs['queryset'] = User.objects.filter(role='teacher')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    # # Ограничения на добавление/изменение/удаление
    # def has_add_permission(self, request):
    #     return request.user.role == 'teacher'

    # def has_change_permission(self, request, obj=None):
    #     if obj and request.user.role == 'teacher':
    #         return obj.teacher == request.user
    #     return request.user.is_superuser

    # def has_delete_permission(self, request, obj=None):
    #     if obj and request.user.role == 'teacher':
    #         return obj.teacher == request.user
    #     return request.user.is_superuser


# -----------------------
# GroupStudent admin
# -----------------------
@admin.register(GroupStudent)
class GroupStudentAdmin(admin.ModelAdmin):
    list_display = ('group', 'student', 'joined_at')
    search_fields = ('group__name', 'student__username')
    fields = ('group', 'student')  # редактируем только при добавлении
    readonly_fields = ('joined_at', 'deleted_student_name')


# -----------------------
# Homework admin
# -----------------------
@admin.register(Homework)
class HomeworkAdmin(admin.ModelAdmin):
    list_display = ('topic', 'group', 'due_date', 'created_at')
    search_fields = ('topic__title', 'group__name')
    fields = ('group', 'topic', 'due_date')


# -----------------------
# HomeworkResult admin
# -----------------------
@admin.register(HomeworkResult)
class HomeworkResultAdmin(admin.ModelAdmin):
    list_display = ('homework', 'student', 'total_score', 'completed', 'completed_at')
    search_fields = ('student__username', 'homework__topic__title')
    fields = ('homework', 'student')  # только при создании
    readonly_fields = ('total_score', 'completed', 'completed_at',)



from django.contrib import admin
from .models import StudyGroup, GroupStudent, User

# Inline для добавления студентов в группу
class GroupStudentInline(admin.TabularInline):
    model = GroupStudent
    extra = 1
    autocomplete_fields = ['student']  # удобно для поиска учеников по имени/почте

    # Фильтруем, чтобы в списке были только ученики
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'student':
            kwargs["queryset"] = User.objects.filter(role='student')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)



