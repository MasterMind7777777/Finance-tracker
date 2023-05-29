from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class StickyNoteContent(models.Model):
    note = models.OneToOneField('StickyNote', on_delete=models.CASCADE, related_name='content')
    html_content = models.TextField()

    def __str__(self):
        return self.html_content

class StickyNote(models.Model):
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title

class Board(models.Model):
    name = models.CharField(max_length=255)
    sticky_notes = models.ManyToManyField(StickyNote, through='BoardStickyNote')

    def __str__(self):
        return self.name

class BoardStickyNote(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    sticky_note = models.ForeignKey(StickyNote, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    position_x = models.IntegerField()
    position_y = models.IntegerField()
    given_title = models.CharField(max_length=100, null=True)

    def __str__(self):
        return f'{self.board.name} - {self.sticky_note.title}'
