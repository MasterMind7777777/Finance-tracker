import pytest
from django.urls import reverse
from django.test import Client
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from users.models import FriendRequest
from transactions.utils import compare_spending
from django.db import transaction
from transactions.models import Transaction, Category
from decimal import Decimal
from django.core.exceptions import ValidationError

User = get_user_model()

@pytest.fixture
def client():
    return Client()

@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(username='testuser', password='12345')

@pytest.fixture
def user1(db):
    return User.objects.create_user(username='testuser1', password='12345')

@pytest.fixture
def user2(db):
    return User.objects.create_user(username='testuser2', password='12345')

@pytest.fixture
def category(db, user):
    return Category.objects.create(user=user, name='Groceries', type=Category.EXPENSE)

@pytest.fixture
def friend_category(db, user1):
    return Category.objects.create(user=user1, name='Groceries Shopping', type=Category.EXPENSE)

@pytest.fixture
def friend_category2(db, user2):
    return Category.objects.create(user=user2, name='Food Shopping', type=Category.EXPENSE)

@pytest.fixture
def transactions(db, user, category):
    Transaction.objects.bulk_create([
        Transaction(user=user, title='tomato', category=category, date=timezone.now() - timezone.timedelta(days=i), amount=Decimal(10)) for i in range(10)
    ])

@pytest.fixture
def friend_transactions(db, user1, friend_category):
    Transaction.objects.bulk_create([
        Transaction(user=user1, title='tomato', category=friend_category, date=timezone.now() - timezone.timedelta(days=i), amount=Decimal(20)) for i in range(10)
    ])

@pytest.fixture
def friend_transactions2(db, user2, friend_category2):
    Transaction.objects.bulk_create([
        Transaction(user=user2, title='tomato', category=friend_category2, date=timezone.now() - timezone.timedelta(days=i), amount=Decimal(30)) for i in range(10)
    ])

def test_signup_view(client):
    response = client.get(reverse('users:signup'))
    assert response.status_code == 200

def test_user_login_view(client, user):
    response = client.post(reverse('users:login'), {'username': 'testuser', 'password': '12345'})
    assert response.status_code == 302

def test_user_logout_view(client, user):
    client.login(username='testuser', password='12345')
    response = client.get(reverse('users:logout'))
    assert response.status_code == 302

def test_dashboard_view(client, user):
    client.login(username='testuser', password='12345')
    response = client.get(reverse('users:dashboard'))
    assert response.status_code == 200

from django.db import transaction

def test_friend_request_model(client, user1, user2):
    # Test friend request creation
    friend_request = FriendRequest.objects.create(
        from_user=user1,
        to_user=user2,
    )
    assert friend_request.from_user == user1
    assert friend_request.to_user == user2
    assert not friend_request.accepted

    # Test unique friend request constraint
    with transaction.atomic():
        try:
            FriendRequest.objects.create(
                from_user=user1,
                to_user=user2,
            )
            assert False  # Assertion failure if duplicate friend request is created
        except Exception:
            assert True  # Exception is raised as expected
    
    # Test unique friend request constraint swap users
    with transaction.atomic():
        try:
            fr = FriendRequest.objects.create(
                from_user=user2,
                to_user=user1,
            )
            assert False  # Assertion failure if duplicate friend request is created
        except Exception:
            assert True  # Exception is raised as expected

    friend_request.accept()

    friend_request.refresh_from_db()
    assert friend_request.accepted

    # Test declining friend request
    friend_request.decline()
    try:
        FriendRequest.objects.get(pk=friend_request.pk)
        assert False  # Assertion failure if friend request is found
    except FriendRequest.DoesNotExist:
        assert True  # Friend request is deleted as expected

# Test user viewset
def test_user_detail(api_client, user1):
    api_client.login(username=user1.username, password='12345')
    url = reverse('api_v1:user-detail', kwargs={'pk': user1.pk})
    response = api_client.get(url)
    assert response.status_code == 200

def test_user_profile(api_client, user1):
    api_client.login(username=user1.username, password='12345')
    url = reverse('api_v1:user-profile', kwargs={'pk': user1.pk})
    response = api_client.get(url)
    assert response.status_code == 200

def test_user_social_media_accounts(api_client, user1):
    api_client.login(username=user1.username, password='12345')
    
    # Create a social media account
    create_url = reverse('api_v1:user-social-media-accounts', kwargs={'pk': user1.pk})
    create_data = {
        'platform': 'Twitter',
        'username': 'user1_twitter'
    }
    create_response = api_client.post(create_url, create_data)
    assert create_response.status_code == 201
    
    # Retrieve the social media accounts
    get_url = reverse('api_v1:user-social-media-accounts', kwargs={'pk': user1.pk})
    get_response = api_client.get(get_url)
    assert get_response.status_code == 200
    
    # Verify the retrieved social media account
    accounts = get_response.json()
    assert len(accounts) == 1
    account = accounts[0]
    assert account['platform'] == 'Twitter'
    assert account['username'] == 'user1_twitter'

def test_user_sent_friend_requests(api_client, user1):
    api_client.login(username=user1.username, password='12345')
    url = reverse('api_v1:user-sent-friend-requests', kwargs={'pk': user1.pk})
    response = api_client.get(url)
    assert response.status_code == 200

def test_user_received_friend_requests(api_client, user1):
    api_client.login(username=user1.username, password='12345')
    url = reverse('api_v1:user-received-friend-requests', kwargs={'pk': user1.pk})
    response = api_client.get(url)
    assert response.status_code == 200

def test_user_accept_friend_request(api_client, user1, user2):
    friend_request = FriendRequest.objects.create(from_user=user1, to_user=user2)
    api_client.login(username=user2.username, password='12345')
    url = reverse('api_v1:user-accept', kwargs={'pk': user1.pk})
    response = api_client.post(url)
    assert response.status_code == 200
    friend_request.refresh_from_db()
    assert friend_request.accepted == True

def test_user_decline_friend_request(api_client, user1, user2):
    friend_request = FriendRequest.objects.create(from_user=user1, to_user=user2)
    api_client.login(username=user2.username, password='12345')
    url = reverse('api_v1:user-decline', kwargs={'pk': user1.pk})
    response = api_client.post(url)
    assert response.status_code == 200
    assert not FriendRequest.objects.filter(pk=friend_request.pk).exists()

def test_compare_spending(db, user, user1, user2, category, friend_category, 
                          friend_category2, transactions, friend_transactions, 
                          friend_transactions2, api_client):
    
    FriendRequest.objects.create(from_user= user, to_user=user1, accepted=True)
    FriendRequest.objects.create(from_user= user, to_user=user2, accepted=True)
    # Test category not owned by user 
    try:
        result = compare_spending(user.id, [user1.id], friend_category.id)
        assert False
    except ValidationError:
        assert True

    # Test single friend
    result = compare_spending(user.id, [user1.id], category.id)
    assert result['user_total'] == Decimal(100)
    assert result['friends_avg'] == Decimal(200)
    assert result['difference'] == Decimal(-100)
    # Testing friends' spending
    assert result['friends_spending'] == {user1.id: Decimal('200.00')}
    # Testing number of transactions made by friends
    assert result['friends_num_transactions'] == {user1.id: 10}
    # Testing average transaction amount of friends
    assert result['friends_avg_transactions'] == {user1.id: Decimal('20.00')}

    # Test multiple friends
    result = compare_spending(user.id, [user1.id, user2.id], category.id)
    assert result['user_total'] == Decimal(100)
    assert result['friends_avg'] == Decimal(250)
    assert result['difference'] == Decimal(-150)
    # Testing friends' spending
    assert result['friends_spending'] == {user1.id: Decimal('200.00'), user2.id: Decimal('300.00')}
    # Testing number of transactions made by friends
    assert result['friends_num_transactions'] == {user1.id: 10, user2.id: 10}
    # Testing average transaction amount of friends
    assert result['friends_avg_transactions'] == {user1.id: Decimal('20.00'), user2.id: Decimal('30.00')}

    # Test friends only validation
    nonfriend_user = User.objects.create_user(username='test non friend user', password='12345')
    try:
        result = compare_spending(user.id, [user1.id, user2.id, nonfriend_user.id], category.id)
        assert False
    except ValidationError:
        assert True

    # Test api endpoint
    api_client.force_authenticate(user=user)
    data = {
            "friends_ids": [user1.id, user2.id],
            "period_days": 30
        }
    response = api_client.post(reverse('api_v1:category-compare-spending', kwargs={"pk": category.id}), data, format='json')
    assert response.status_code == 200
    response_data = response.json()
    assert 'user_total' in response_data
    assert response_data['user_total'] == Decimal(100)
    assert 'user_num_transactions' in response_data
    assert response_data['friends_num_transactions'] == {str(user1.id): 10, str(user2.id): 10}
    assert 'user_avg_transaction' in response_data
    assert response_data['friends_avg_transactions'] == {str(user1.id): Decimal('20.00'), str(user2.id): Decimal('30.00')}
    assert 'friends_avg' in response_data
    assert response_data['friends_avg'] == Decimal(250)
    assert 'difference' in response_data
    assert response_data['difference'] == Decimal(-150)
    assert 'friends_spending' in response_data
    assert response_data['friends_spending'] == {str(user1.id): Decimal('200.00'), str(user2.id): Decimal('300.00')}
    assert 'friends_num_transactions' in response_data
    assert response_data['friends_num_transactions'] == {str(user1.id): 10, str(user2.id): 10}
    assert 'friends_avg_transactions' in response_data
    assert result['friends_avg_transactions'] == {user1.id: Decimal('20.00'), user2.id: Decimal('30.00')}
