from django.contrib import admin
from .models import NutritionProgram
from .models import WorkoutProgram, Blogs


@admin.register(NutritionProgram)
class NutritionProgramAdmin(admin.ModelAdmin):
    list_display = ('title', 'proteins', 'fats', 'carbohydrates', 'kcal')


admin.site.register(WorkoutProgram)
admin.site.register(Blogs)
