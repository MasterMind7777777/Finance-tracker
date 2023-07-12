from django.urls import reverse
import pytest
from transactions.models import Transaction, Category
from capital.models import SavingGoal
from rest_framework.test import APIClient
from django.test import Client
from django.contrib.auth import get_user_model
from api_v1.serializers import SavingGoalSerializer

User = get_user_model()

@pytest.fixture
def client():
    return Client()

@pytest.fixture
def client1():
    return Client()

@pytest.fixture
def client2():
    return Client()

@pytest.fixture
def user(db):
    user = User.objects.create_user(username='testuser', password='12345')
    return user

@pytest.fixture
def user1(db):
    user = User.objects.create_user(username='testuser1', password='12345')
    return user

@pytest.fixture
def user2(db):
    user = User.objects.create_user(username='testuser2', password='123456')
    return user

@pytest.mark.django_db
def test_goal_setting_and_tracking(client, user):
    client.login(username='testuser', password='12345')

    # Create a saving category
    saving_category = Category.objects.create(
        user=user,
        name="Saving for vacation",
        type=Category.SAVING
    )

    # Create a saving goal
    saving_goal = SavingGoal.objects.create(
        name="Save for vacation",
        target_amount=2000,
    )

    # Associate the category with the saving goal
    saving_goal.categories.add(saving_category)

    # Associate the user with the saving goal
    saving_goal.users.add(user)

    # Create some transactions and check goal progress after each one
    transactions = [500, 300, 200]  # amounts of transactions
    for i, amount in enumerate(transactions, start=1):
        Transaction.objects.create(
            user=user,
            title=f"Saving {i}",
            amount=amount,
            category=saving_category
        )

        # Refresh saving goal from database to get current amount after the transaction
        saving_goal.refresh_from_db()

        # Check the goal progress
        expected_progress = (sum(transactions[:i]) / saving_goal.target_amount) * 100
        actual_progress = (saving_goal.current_amount / saving_goal.target_amount) * 100

        assert actual_progress == pytest.approx(expected_progress), f"Fail at transaction {i}"

@pytest.mark.django_db
def test_saving_goal_sharing_with_transactions_and_categories(client, user, user2):
    client.login(username='testuser1', password='12345')

    # Create a saving category for each user
    saving_category_user = Category.objects.create(
        user=user,
        name="Saving for vacation",
        type=Category.SAVING
    )

    saving_category_user2 = Category.objects.create(
        user=user2,
        name="Saving for vacation",
        type=Category.SAVING
    )

    # Create a saving goal
    saving_goal = SavingGoal.objects.create(
        name="Save for vacation",
        target_amount=2000,
    )

    # Associate the categories with the saving goal
    saving_goal.categories.add(saving_category_user, saving_category_user2)

    # Associate the users with the saving goal
    saving_goal.users.add(user, user2)

    # Check if the saving goal is now associated with both users
    assert saving_goal in SavingGoal.objects.filter(users__in=[user.id, user2.id])

    # Refresh the saving goal from the database
    saving_goal.refresh_from_db()

    # Check if both users are now associated with the saving goal
    assert user in saving_goal.users.all()
    assert user2 in saving_goal.users.all()

    # Create transactions from both users
    transactions_user = [500, 300, 200]
    transactions_user2 = [400, 100, 300]
    for i, (amount_user, amount_user2) in enumerate(zip(transactions_user, transactions_user2), start=1):
        Transaction.objects.create(
            user=user,
            title=f"Saving {i} by user1",
            amount=amount_user,
            category=saving_category_user
        )
        Transaction.objects.create(
            user=user2,
            title=f"Saving {i} by user2",
            amount=amount_user2,
            category=saving_category_user2
        )

        # Refresh saving goal from database to get current amount after the transaction
        saving_goal.refresh_from_db()

        # Check the goal progress after both user's transactions
        expected_progress = (sum(transactions_user[:i] + transactions_user2[:i]) / saving_goal.target_amount) * 100
        actual_progress = (saving_goal.current_amount / saving_goal.target_amount) * 100

        assert actual_progress == pytest.approx(expected_progress), f"Fail at transaction {i}"

@pytest.mark.django_db
def test_saving_goal_crud(client, client2, user, user1, user2):

    category1 = Category.objects.create(user=user1, name="Saving for vacation", type=Category.SAVING)
    category1_1 = Category.objects.create(user=user1, name="Saving for house", type=Category.SAVING)
    category2 = Category.objects.create(user=user2, name="Saving for car", type=Category.SAVING)

    saving_goal_data = {
        'name': 'SavingGoal1',
        'target_amount': 1000,
        'users': [user1.id],
        'categories': [category1.id]
    }
    # Log in
    client = APIClient()
    client2 = APIClient()
    client.force_authenticate(user1)
    client2.force_authenticate(user2)

    # Test Creating a SavingGoal
    response = client.post(reverse('api_v1:savinggoal-list'), saving_goal_data, format='json')
    assert response.status_code == 201
    assert SavingGoal.objects.count() == 1
    saving_goal = SavingGoal.objects.get(id=response.data['id'])
    assert saving_goal.name == saving_goal_data['name']

    # Test Retrieving a SavingGoal
    response = client.get(reverse('api_v1:savinggoal-detail', kwargs={'pk': saving_goal.id}))
    assert response.status_code == 200
    assert response.data == SavingGoalSerializer(saving_goal).data

    # Test Updating a SavingGoal
    update_data = {'name': 'UpdatedSavingGoal'}
    response = client.patch(reverse('api_v1:savinggoal-detail', kwargs={'pk': saving_goal.id}), update_data, format='json')
    assert response.status_code == 200
    saving_goal.refresh_from_db()
    assert saving_goal.name == update_data['name']

    # Test Adding a User to a SavingGoal
    response = client.post(reverse('api_v1:savinggoal-add-users', kwargs={'pk': saving_goal.id}), {'users': [user2.id]}, format='json')
    assert response.status_code == 200
    saving_goal.refresh_from_db()
    assert user2 in saving_goal.users.all()

    # Try adding a user to the SavingGoal by non creator
    response = client2.post(reverse('api_v1:savinggoal-add-users', kwargs={'pk': saving_goal.id}), {'users': [user.id]}, format='json')
    assert response.status_code == 403  # Expecting a Forbidden status code (non-creator trying to add users)

    # Ensure the user is not added to the SavingGoal
    saving_goal.refresh_from_db()
    assert user not in saving_goal.users.all()

    # Test Removing a User from a SavingGoal
    response = client.post(reverse('api_v1:savinggoal-remove-users', kwargs={'pk': saving_goal.id}), {'users': [user2.id]}, format='json')
    assert response.status_code == 200
    saving_goal.refresh_from_db()
    assert user2 not in saving_goal.users.all()

    # Test Adding a Category to a SavingGoal
    response = client.post(reverse('api_v1:savinggoal-add-categories', kwargs={'pk': saving_goal.id}), {'categories': [category1_1.id]}, format='json')
    assert response.status_code == 200
    saving_goal.refresh_from_db()
    assert category1 in saving_goal.categories.all()

    # Test Removing a Category from a SavingGoal
    response = client.post(reverse('api_v1:savinggoal-remove-categories', kwargs={'pk': saving_goal.id}), {'categories': [category1_1.id]}, format='json')
    assert response.status_code == 200
    saving_goal.refresh_from_db()
    assert category1_1 not in saving_goal.categories.all()

    # Test Adding a User to a SavingGoal back again
    response = client.post(reverse('api_v1:savinggoal-add-users', kwargs={'pk': saving_goal.id}), {'users': [user2.id]}, format='json')
    assert response.status_code == 200
    saving_goal.refresh_from_db()
    assert user2 in saving_goal.users.all()

    # Try adding a category to the SavingGoal by non owner of the category
    response = client2.post(reverse('api_v1:savinggoal-add-categories', kwargs={'pk': saving_goal.id}), {'categories': [category1_1.id]}, format='json')
    assert response.status_code == 403  # Expecting a Forbidden status code (non-owner trying to add category)

    # Ensure the category is not added to the SavingGoal
    saving_goal.refresh_from_db()
    assert category2 not in saving_goal.categories.all()

    # Try removing the category from the saving goal by non-owner user2
    response = client2.post(reverse('api_v1:savinggoal-remove-categories', kwargs={'pk': saving_goal.id}), {'categories': [category1.id]}, format='json')

    # Assert that the request is forbidden
    assert response.status_code == 403

    # Ensure the category is not removed from the saving goal
    saving_goal.refresh_from_db()
    assert category1 in saving_goal.categories.all()

    # Create new users and categories for these tests
    user3 = User.objects.create_user(username='user3', password='testpass123')
    user4 = User.objects.create_user(username='user4', password='testpass123')
    category3 = Category.objects.create(user=user3, name="Saving for bike", type=Category.SAVING)
    category4 = Category.objects.create(user=user4, name="Saving for laptop", type=Category.SAVING)
    category5 = Category.objects.create(user=user1, name="Saving for bike", type=Category.SAVING)
    category6 = Category.objects.create(user=user1, name="Saving for laptop", type=Category.SAVING)

    # Test Adding Multiple Categories to a SavingGoal
    categories_to_add = [category5.id, category6.id]
    response = client.post(reverse('api_v1:savinggoal-add-categories', kwargs={'pk': saving_goal.id}), {'categories': categories_to_add}, format='json')
    assert response.status_code == 200
    saving_goal.refresh_from_db()
    # extract the 'id' attribute from all Category objects in the QuerySet
    saved_category_ids = [category.id for category in saving_goal.categories.all()]
    assert all(category in saved_category_ids for category in categories_to_add)

    # Test Removing Multiple Categories from a SavingGoal
    response = client.post(reverse('api_v1:savinggoal-remove-categories', kwargs={'pk': saving_goal.id}), {'categories': categories_to_add}, format='json')
    assert response.status_code == 200
    saving_goal.refresh_from_db()
    # extract the 'id' attribute from all Category objects in the QuerySet
    saved_category_ids = [category.id for category in saving_goal.categories.all()]
    assert not any(category in saved_category_ids for category in categories_to_add)

    # Test Adding Multiple Categories to a SavingGoal with one category that does not belong to the user
    categories_to_add_bad = [category5.id, category6.id, category3.id]
    response = client.post(reverse('api_v1:savinggoal-add-categories', kwargs={'pk': saving_goal.id}), {'categories': categories_to_add_bad}, format='json')
    assert response.status_code == 403  # Expecting a Forbidden status code (non-owner trying to add category)

    # Ensure the category is not added to the SavingGoal
    saving_goal.refresh_from_db()
    saved_category_ids = [category.id for category in saving_goal.categories.all()]
    assert not any(category in saved_category_ids for category in categories_to_add_bad)

    # Add some categories to the SavingGoal that belong to the user
    saving_goal.categories.add(category3, category4, category5, category6)
    saving_goal.refresh_from_db()
    assert category3 in saving_goal.categories.all()
    assert category4 in saving_goal.categories.all()
    assert category5 in saving_goal.categories.all()
    assert category6 in saving_goal.categories.all()

    # Try to remove multiple categories from the SavingGoal, one of which does not belong to the user
    categories_to_remove_bad = [category5.id, category3.id]
    response = client.post(reverse('api_v1:savinggoal-remove-categories', kwargs={'pk': saving_goal.id}), {'categories': categories_to_remove_bad}, format='json')
    assert response.status_code == 403  # Expecting a Forbidden status code (non-owner trying to remove category)

    # Ensure the categories are not removed from the SavingGoal
    saving_goal.refresh_from_db()
    saved_category_ids = [category.id for category in saving_goal.categories.all()]
    assert category3.id in saved_category_ids  # Ensure the category that does not belong to the user is not removed

    # Again for the other categories
    categories_to_remove_bad = [category6.id, category4.id]
    response = client.post(reverse('api_v1:savinggoal-remove-categories', kwargs={'pk': saving_goal.id}), {'categories': categories_to_remove_bad}, format='json')
    assert response.status_code == 403  # Expecting a Forbidden status code (non-owner trying to remove category)

    # Ensure the categories are not removed from the SavingGoal
    saving_goal.refresh_from_db()
    saved_category_ids = [category.id for category in saving_goal.categories.all()]
    assert category4.id in saved_category_ids  # Ensure the category that does not belong to the user is not removed

    # Test Adding Multiple Users to a SavingGoal
    users_to_add = [user3.id, user4.id]
    response = client.post(reverse('api_v1:savinggoal-add-users', kwargs={'pk': saving_goal.id}), {'users': users_to_add}, format='json')
    assert response.status_code == 200
    saving_goal.refresh_from_db()
    # extract the 'id' attribute from all User objects in the QuerySet
    saved_user_ids = [user.id for user in saving_goal.users.all()]
    assert all(user in saved_user_ids for user in users_to_add)

    # Test Removing Multiple Users from a SavingGoal
    response = client.post(reverse('api_v1:savinggoal-remove-users', kwargs={'pk': saving_goal.id}), {'users': users_to_add}, format='json')
    assert response.status_code == 200
    saving_goal.refresh_from_db()
    # extract the 'id' attribute from all User objects in the QuerySet
    saved_user_ids = [user.id for user in saving_goal.users.all()]
    assert not any(user in saved_user_ids for user in users_to_add)

    # Test Deleting a SavingGoal
    response = client.delete(reverse('api_v1:savinggoal-detail', kwargs={'pk': saving_goal.id}))
    assert response.status_code == 204
    assert SavingGoal.objects.count() == 0
