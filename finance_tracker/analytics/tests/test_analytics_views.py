import random
import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from analytics.models import Board, StickyNote, BoardStickyNote, StickyNoteContent
from analytics.utils import create_financial_health
from analytics.models import FinancialHealth
from transactions.models import Transaction, Category
import json
from rest_framework.test import APIClient

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

@pytest.mark.django_db
def test_savings_opportunities(client, user):
    # Create test user and transactions
    client.force_login(user)
    # Create an instance of APIClient
    client = APIClient()
    # Force login using create_user
    client.force_authenticate(user=user)

    category = Category.objects.create(name="entertainment", user=user)

    num_of_test_transactions = 8000
    transaction_names = [f"transaction{i}" for i in range(1, num_of_test_transactions + 1)]


    # Set the configuration parameters
    tomato_flight_percentage = 0.5  # Percentage of times "tomato" is followed by "flight"

    # Create frequent transactions
    frequent_transactions = [
        Transaction(title="movie", user=user, category=category, amount=70),
        Transaction(title="burger", user=user, category=category, amount=50)
    ] * 2000

    # Create additional transactions with "flight" or "tomato" according to the pattern
    additional_transactions = []
    num_loops = 2000  # Number of loops for inserting "flight" or "tomato"

    chosen_title = 'tomato'
    prev_chosen_title = 'flight'
    for _ in range(num_loops):
        additional_transactions.append(Transaction(title=chosen_title, user=user, category=category, amount=random.randint(50, 200)))

        # Determine the next title based on the percentage
        if random.random() > tomato_flight_percentage:
            chosen_title = random.sample(transaction_names, 1)
            transaction_names.remove(chosen_title[0])
        elif chosen_title == 'tomato':
            chosen_title = 'flight'
            prev_chosen_title = 'tomato'
        elif chosen_title == 'flight':
            chosen_title = 'tomato'
            prev_chosen_title = 'flight'
        else:
            chosen_title = prev_chosen_title


    # Create infrequent transactions with random amounts of transactions
    infrequent_transactions = []
    for _ in range(10):
        infrequent_transactions.extend([
            Transaction(title=random.choice(transaction_names), user=user, category=category, amount=random.randint(10, 100))
            for _ in range(random.randint(1, 5))
        ])

    # Add all transactions to the database
    Transaction.objects.bulk_create(frequent_transactions + additional_transactions + infrequent_transactions)

    url = reverse('api_v1:transaction-savings_opportunities', kwargs={'category_id': category.id})
    response = client.get(url)

    assert response.status_code == 200
    opportunities = response.json()

    assert isinstance(opportunities, list)
    assert len(opportunities) > 0

    opportunity = opportunities[0]
    assert opportunity["category"] == "entertainment"
    assert opportunity["potential_savings"] > 0
    assert "correlations" in opportunity
    assert "association_rules" in opportunity

    correlations = opportunity["correlations"]
    assert isinstance(correlations, list)
    assert all(isinstance(c, tuple) and len(c) == 2 for c in correlations)

    association_rules = opportunity["association_rules"]
    assert isinstance(association_rules, list)
    assert all(isinstance(rule, dict) for rule in association_rules)

    print(association_rules)
    # New tests for frequent itemsets and infrequent itemsets
    assert any(rule['antecedents'] == ['movie'] and rule['consequents'] == ['burger'] for rule in association_rules)
    assert not any(rule['antecedents'] == ['tomato'] and rule['consequents'] == ['flight'] for rule in association_rules)

def test_financial_health_dashboard(client, user):
    # Create test user and transactions
    client.force_login(user)
    # Create an instance of APIClient
    client = APIClient()
    # Force login using create_user
    client.force_authenticate(user=user)

    categories = [
        ('Income', Category.INCOME),
        ('Expense', Category.EXPENSE),
        ('Saving', Category.SAVING),
        ('Investment', Category.INVESTMENT)
    ]

    category_objects = []

    # Create Category objects
    for category_name, category_type in categories:
        category = Category.objects.create(
            user=user,
            name=category_name,
            type=category_type
        )
        category_objects.append(category)

    transactions = [
        ('Income Transaction 1', category_objects[0], 5000.0),
        ('Income Transaction 2', category_objects[0], 3000.0),
        ('Expense Transaction 1', category_objects[1], 1000.0),
        ('Expense Transaction 2', category_objects[1], 2000.0),
        ('Saving Transaction 1', category_objects[2], 500.0),
        ('Saving Transaction 2', category_objects[2], 500.0),
        ('Investment Transaction 1', category_objects[3], 1500.0),
        ('Investment Transaction 2', category_objects[3], 500.0)
    ]

    transaction_objects = []

    # Create Transaction objects
    for title, category, amount in transactions:
        transaction = Transaction.objects.create(
            user=user,
            title=title,
            amount=amount,
            category=category,
            date=timezone.now()
        )
        transaction_objects.append(transaction)

    # Form financial health object
    financial_health = create_financial_health(user.pk)

        
    # Request
    response = client.get(reverse('api_v1:financial-health'))

    # Assertions
    assert response.status_code == 200
    data = response.json()

    expected_keys = ['user', 'income', 'expenditure', 'savings', 'investments', 'score', 'advice']
    for key in expected_keys:
        assert key in data

    assert data['user'] == 1
    assert float(data['income']) == 8000.0
    assert float(data['expenditure']) == 3000.0
    assert float(data['savings']) == 1000.0
    assert float(data['investments']) == 2000.0
    assert data['score'] is not None
    assert isinstance(data['advice'], list)
