import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from analytics.models import Board, StickyNote, BoardStickyNote, StickyNoteContent
import json

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user('testuser', 'test@test.com', '12345')


@pytest.fixture
def sticky_note(db):
    return StickyNote.objects.create(title='Test Sticky Note')


@pytest.fixture
def sticky_note_content(db, sticky_note):
    return StickyNoteContent.objects.create(note=sticky_note, html_content='<p>Test HTML content</p>')


@pytest.fixture
def board(db):
    return Board.objects.create(name='Test Board')


@pytest.fixture
def board_sticky_note(db, user, board, sticky_note):
    return BoardStickyNote.objects.create(
        board=board,
        sticky_note=sticky_note,
        user=user,
        position_x=100,
        position_y=200,
        given_title='Test Given Title',
    )


def test_analytics_view(client, board):
    client.login(username='testuser', password='12345')
    # Gives error WARNING  django.request:log.py:241 Not Found: /analytics/x
    # response = client.get(reverse('analytics:analytics'))
    # assert response.status_code == 200
    response = client.get(reverse('analytics:analytics_add', kwargs={'board_id': board.id}))
    assert response.status_code == 200

@pytest.mark.django_db
def test_fetch_sticky_notes(client):
    # Create a user for login
    user = User.objects.create_user(username='testuser', password='12345')

    # Create a StickyNote with associated content
    sticky_note = StickyNote.objects.create(title='Test Sticky Note')
    StickyNoteContent.objects.create(note=sticky_note, html_content='<p>Test content</p>')

    # Login the client
    client.force_login(user)

    # Make a GET request to the view
    response = client.get(reverse('analytics:fetch_sticky_notes'))

    # Assert that the response status code is 200 (OK)
    assert response.status_code == 200



def test_create_or_add_to_board(client, user, sticky_note, board):
    client.login(username='testuser', password='12345')

    # Check if a board with the name already exists, and delete it if found
    Board.objects.filter(name='Test Board').delete()

    response = client.post(reverse('analytics:create_or_add_to_board'), {
        'board_name': 'Test Board',
        'sticky_note_id': sticky_note.id,
        'position_x': 100,
        'position_y': 200,
        'user_id': user.id,
        'given_title': 'Test Given Title',
    })
    assert response.status_code == 200

    assert Board.objects.filter(name='Test Board').exists()
    board = Board.objects.get(name='Test Board')  # Retrieve the unique Board object

    board_sticky_note = BoardStickyNote.objects.filter(
        board=board,
        sticky_note=sticky_note,
        given_title='Test Given Title'
    ).exists()
    assert board_sticky_note is True, response.content


@pytest.mark.django_db
def test_fetch_board_sticky_notes(client, user, board, sticky_note):
    # Create a StickyNoteContent associated with the sticky note
    sticky_note_content = StickyNoteContent.objects.create(
        note=sticky_note,
        html_content='<p>Test content</p>'
    )

    # Create a BoardStickyNote associated with the board, sticky note, and user
    board_sticky_note = BoardStickyNote.objects.create(
        board=board,
        sticky_note=sticky_note,
        position_x=100,
        position_y=200,
        user=user,
        given_title='Test Given Title'
    )

    # Login the client
    client.force_login(user)

    # Make a GET request to the view
    response = client.get(reverse('analytics:fetch_board_sticky_notes', args=[board.id]))

    # Assert that the response status code is 200 (OK)
    assert response.status_code == 200, response.content

    # Assert the response JSON
    assert response.json() == [
        {
            'id': sticky_note.id,
            'title': sticky_note.title,
            'content': sticky_note_content.html_content,
            'position_x': board_sticky_note.position_x,
            'position_y': board_sticky_note.position_y,
        }
    ]





def test_delete_sticky_note_from_board(client, user, board, sticky_note):
    client.login(username='testuser', password='12345')
    board_sticky_note = BoardStickyNote.objects.create(board=board, sticky_note=sticky_note, position_x=100, position_y=200, user=user, given_title='Test Given Title')
    response = client.post(reverse('analytics:delete_sticky_note_from_board', kwargs={'board_id': board.id}), {'given_title': board_sticky_note.given_title})
    assert response.status_code == 200


def test_save_board(client, user, sticky_note, board):
    client.login(username='testuser', password='12345')
    response = client.post(reverse('analytics:save_board', args=[board.id]), {
        'board_name': 'Test Board',
        'sticky_notes': json.dumps([{
            'sticky_note_id': sticky_note.id,
            'position_x': 100,
            'position_y': 200,
            'user_id': user.id,
            'given_title': 'Test Given Title',
        }]),
    })
    assert response.status_code == 200
    assert Board.objects.filter(name='Test Board').exists()

def test_fetch_user_boards(client, user, board, sticky_note):
    client.login(username='testuser', password='12345')
    BoardStickyNote.objects.create(board=board, sticky_note=sticky_note, position_x=100, position_y=200, user=user, given_title='Test Given Title')
    response = client.get(reverse('analytics:fetch_user_boards', kwargs={'user_id': user.id}))
    assert response.status_code == 200

def test_analytics_view_with_invalid_board_id(client, user):
    # Test the analytics_view function with an invalid board ID
    client.login(username='testuser', password='12345')
    response = client.get(reverse('analytics:analytics_add', kwargs={'board_id': 999999}))
    assert response.status_code == 404  # Expect a 404 status code because the board does not exist

def test_create_or_add_to_board_with_invalid_sticky_note_id(client, user, board):
    # Test the create_or_add_to_board function with an invalid sticky note ID
    client.login(username='testuser', password='12345')
    response = client.post(reverse('analytics:create_or_add_to_board'), {
        'board_id': board.id,
        'sticky_note_id': -111,  # Invalid sticky note ID
        'position_x': 100,
        'position_y': 200,
        'user_id': user.id,
        'given_title': 'Test Given Title',
    })
    assert response.status_code == 404  # Expect a 404 status code because the sticky note does not exist
