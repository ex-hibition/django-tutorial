from django.contrib import admin

from .models import Question

"""Question が admin インタフェースを持つことを admin に伝える"""
admin.site.register(Question)
