from django.contrib import admin
from .models import Exercise, Program, Workout, WorkoutExercise, WorkoutSession, ExerciseLog


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ("name", "related_skill")
    search_fields = ("name",)


class WorkoutExerciseInline(admin.TabularInline):
    model = WorkoutExercise
    extra = 1


@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin):
    list_display = ("title", "program", "estimated_duration_minutes", "order_in_program")
    inlines = [WorkoutExerciseInline]


class WorkoutInline(admin.TabularInline):
    model = Workout
    extra = 1


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ("name", "target_skill", "duration_weeks", "days_per_week")
    inlines = [WorkoutInline]


@admin.register(WorkoutSession)
class WorkoutSessionAdmin(admin.ModelAdmin):
    list_display = ("user", "workout", "started_at", "is_completed")
    list_filter = ("is_completed",)


admin.site.register(ExerciseLog)
