from django.contrib import admin
from .models import StickyNote, StickyNoteContent

@admin.register(StickyNote)
class StickyNoteAdmin(admin.ModelAdmin):
    list_display = ['title',]

@admin.register(StickyNoteContent)
class StickyNoteContentAdmin(admin.ModelAdmin):
    list_display = ['note', 'html_content']