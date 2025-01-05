from django.contrib import admin
from django_llm_poison.models import MarkovModel

admin.site.register(MarkovModel, admin.ModelAdmin)
