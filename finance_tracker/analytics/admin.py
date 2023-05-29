from django.contrib import admin
from .models import StickyNote, StickyNoteContent, Board, BoardStickyNote

class BoardStickyNoteInline(admin.TabularInline):
    model = BoardStickyNote

@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ['name']
    inlines = [BoardStickyNoteInline]

@admin.register(StickyNote)
class StickyNoteAdmin(admin.ModelAdmin):
    list_display = ['title']

@admin.register(StickyNoteContent)
class StickyNoteContentAdmin(admin.ModelAdmin):
    list_display = ['note', 'html_content']

@admin.register(BoardStickyNote)
class BoardStickyNoteAdmin(admin.ModelAdmin):
    list_display = ['board', 'sticky_note', 'user', 'position_x', 'position_y', 'given_title']
