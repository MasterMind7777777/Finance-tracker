# models.py

from django.db import models

class StickyNoteContent(models.Model):
    note = models.OneToOneField('StickyNote', on_delete=models.CASCADE, related_name='content')
    html_content = models.TextField()

    def __str__(self):
        return self.html_content

class StickyNote(models.Model):
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title
