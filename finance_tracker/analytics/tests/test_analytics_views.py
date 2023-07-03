import pytest
from django.test import Client
from django.urls import reverse
from analytics.models import StickyNote, Board, BoardStickyNote
from transactions.models import Transaction, Category
from budgets.models import CategoryBudget
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.fixture
def client():
    return Client()

@pytest.fixture
def user():
    return User.objects.create_user(username='testuser', password='12345')

@pytest.fixture
def category():
    return Category.objects.create(name='Test Category', type='expense')

@pytest.fixture
def transaction(user, category):
    return Transaction.objects.create(user=user, category=category, amount=100)

@pytest.fixture
def sticky_note():
    return StickyNote.objects.create(title='Test Sticky Note', content='Test Content')

@pytest.fixture
def board(user):
    return Board.objects.create(user=user, name='Test Board')

@pytest.fixture
def board_sticky_note(board, sticky_note):
    return BoardStickyNote.objects.create(board=board, sticky_note=sticky_note, position_x=0, position_y=0)

@pytest.mark.django_db
def test_analytics_view(client, user, transaction, sticky_note, board, board_sticky_note):
    client.login(username='testuser', password='12345')
    response = client.get(reverse('analytics:analytics_view'))
    assert response.status_code == 200
    assert 'total_expenses' in response.context
    assert 'monthly_expenses' in response.context
    assert 'category_expenses' in response.context
    assert 'total_income' in response.context
    assert 'monthly_income' in response.context
    assert 'budget_utilization' in response.context
    assert 'transactions' in response.context
    assert 'sticky_notes' in response.context
    assert 'main_board' in response.context

@pytest.mark.django_db
def test_fetch_sticky_notes(client, user, sticky_note):
    client.login(username='testuser', password='12345')
    response = client.get(reverse('analytics:fetch_sticky_notes'))
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]['title'] == 'Test Sticky Note'

@pytest.mark.django_db
def test_create_or_add_to_board(client, user, board, sticky_note):
    client.login(username='testuser', password='12345')
    response = client.post(reverse('analytics:create_or_add_to_board'), {
        'board_id': board.id,
        'sticky_note_id': sticky_note.id,
        'position_x': 0,
        'position_y': 0,
        'given_title': 'Test Title'
    })
    assert response.status_code == 200
    assert response.json()['message'] == 'Sticky note added to the board successfully.'

@pytest.mark.django_db
def test_fetch_board_sticky_notes(client, user, board, board_sticky_note):
    client.login(username='testuser', password='12345')
    response = client.get(reverse('analytics:fetch_board_sticky_notes', args=[board.id]))
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]['position_x'] == 0
    assert response.json()[0]['position_y'] == 0

@pytest.mark.django_db
def test_delete_sticky_note_from_board(client, user, board, board_sticky_note):
    client.login(username='testuser', password='12345')
    response = client.post(reverse('analytics:delete_sticky_note_from_board', args=[board.id]), {
        'given_title': board_sticky_note.given_title
    })
    assert response.status_code == 200
    assert response.json()['message'] == 'Sticky note deleted from the board successfully.'
