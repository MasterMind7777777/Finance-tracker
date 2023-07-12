import re
from django.core.serializers.json import DjangoJSONEncoder
from .models import Category
from django.db.models import Sum, Q, Max, Avg
import calendar
from datetime import date, datetime, timedelta
from .models import Transaction, RecurringTransaction
from django.utils import timezone
from django.contrib.auth import get_user_model
from users.models import FriendRequest
from django.core.exceptions import ValidationError
User = get_user_model()
import nltk

nltk.data.path.append('C:/projects/Finance-tracker/finance_tracker/nltk')
try:
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
except:
    nltk.download('stopwords', download_dir='C:/projects/Finance-tracker/finance_tracker/nltk')
    nltk.download('punkt', download_dir='C:/projects/Finance-tracker/finance_tracker/nltk')
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize

class CategoryEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, Category):
            return str(obj)
        return super().default(obj)

def forecast_expenses(user):
    today = date.today()
    start_of_month = today.replace(day=1)

    # Calculate the total number of days in the month
    total_days_in_month = calendar.monthrange(today.year , today.month)[1]

    # Calculate the actual number of days that have passed in the current month
    days_passed = (today - start_of_month).days + 1

    expenses = Transaction.objects.filter(user=user, date__gte=start_of_month).aggregate(total_expenses=Sum('amount'))
    total_expenses = expenses['total_expenses'] or 0

    # Calculate the average daily expenses
    avg_daily_expenses = total_expenses / days_passed

    # Calculate the forecasted expenses for the remaining days of the month
    forecast_next_month = avg_daily_expenses * total_days_in_month

    return forecast_next_month

def categorize_transaction(transaction_id, user_id):
    # Retrieve the uncategorized transaction
    uncategorized_transaction = Transaction.objects.get(id=transaction_id)

    # Define the available categories based on the user ID
    categories = Category.objects.filter(user=user_id)

    # Extract keywords from the transaction name and description
    transaction_keywords = extract_keywords(uncategorized_transaction.title + ' ' + uncategorized_transaction.description)

    # Find the most suitable category based on the keywords and existing transactions
    chosen_category = find_matching_category(transaction_keywords, categories)

    # Categorize the transaction
    uncategorized_transaction.category = chosen_category
    uncategorized_transaction.save()

def extract_keywords(text):
    # Remove special characters and convert text to lowercase
    cleaned_text = re.sub(r'[^a-zA-Z0-9\s]', '', text.lower())

    # Tokenize the cleaned text into individual words
    words = word_tokenize(cleaned_text)

    # Remove common stop words
    stop_words = set(stopwords.words('english'))
    words = [word for word in words if word not in stop_words]
    return words

def find_matching_category(keywords, categories):
    category_scores = {}

    for category in categories:
        related_transactions = Transaction.objects.filter(category=category)

        # Extract keywords from related transactions
        related_keywords = []
        for transaction in related_transactions:
            related_keywords.extend(extract_keywords(transaction.title + ' ' + transaction.description))

        score = calculate_similarity(keywords, related_keywords)
        category_scores[category] = score

    # Sort the category scores in descending order
    sorted_scores = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)

    # Return the category with the highest score
    
    chosen_category = sorted_scores[0][0]
    return chosen_category

def calculate_similarity(keywords1, keywords2):
    set1 = set(keywords1)
    set2 = set(keywords2)

    # Calculate the intersection of the two sets
    intersection = set1.intersection(set2)

    # Calculate the union of the two sets
    union = set1.union(set2)
    # Calculate the Jaccard similarity coefficient
    similarity = len(intersection) / len(union)

    return similarity

def apply_recurring_transactions():
    # Current date
    current_date = timezone.now().date()

    # Retrieve the latest transaction dates for each recurring transaction
    latest_transaction_dates = Transaction.objects.filter(
        recurring_transaction__isnull=False,
        date__date__lt=current_date
    ).values('recurring_transaction').annotate(latest_date=Max('date__date'))

    # Get the recurring transactions for the latest dates
    recurring_transactions = RecurringTransaction.objects.filter(
        pk__in=[item['recurring_transaction'] for item in latest_transaction_dates]
    )

    # Create a list of transactions to create
    transactions_to_create = []

    for transaction_date in latest_transaction_dates:
        recurring_transaction = next(
            rt for rt in recurring_transactions if rt.pk == transaction_date['recurring_transaction']
        )
        latest_date = transaction_date['latest_date']

        if recurring_transaction.frequency == 'daily' and (current_date - latest_date).days >= 1:
            transactions_to_create.append(create_new_transaction(recurring_transaction))
        elif recurring_transaction.frequency == 'weekly' and (current_date - latest_date).days >= 7:
            transactions_to_create.append(create_new_transaction(recurring_transaction))
        elif recurring_transaction.frequency == 'monthly' and (current_date.month != latest_date.month or current_date.year != latest_date.year):
            transactions_to_create.append(create_new_transaction(recurring_transaction))
        elif recurring_transaction.frequency == 'yearly' and current_date.year != latest_date.year:
            transactions_to_create.append(create_new_transaction(recurring_transaction))

    # Bulk create the new transactions
    Transaction.objects.bulk_create(transactions_to_create)

def create_new_transaction(recurring_transaction):
    # Create a new Transaction instance with the properties from the recurring transaction
    return Transaction(
        user=recurring_transaction.user,
        title=f'Recurring Transaction {recurring_transaction.id}',
        amount=recurring_transaction.amount,
        category=recurring_transaction.category,
        date=timezone.now(),
        recurring_transaction=recurring_transaction
    )

def compare_spending(user_id, friends_ids, category_id, period_days=30):
    user = User.objects.get(pk=user_id)
    try:
        category = Category.objects.get(pk=category_id, user=user)
    except Category.DoesNotExist:
        raise ValidationError(f"{category_id} is not one of categories of current user.")

    # Calculate the start date of the period
    start_date = datetime.now() - timedelta(days=period_days)

    # Get the user's transactions in the category during the period
    user_transactions = Transaction.objects.filter(user=user, category=category, date__gte=start_date)

    # Calculate the total spending of the user in the category during the period
    user_total = sum(transaction.amount for transaction in user_transactions)

    # Calculate the number of transactions and average transaction amount for the user
    user_num_transactions = len(user_transactions)
    user_avg_transaction = user_total / user_num_transactions if user_transactions else 0

    # Get the friends
    # Fetch all accepted friend requests related to current user
    accepted_friend_requests = FriendRequest.objects.filter(
        Q(from_user=user) | Q(to_user=user), 
        accepted=True
    )

    # Extract friend users from accepted friend requests
    friends = set()  # Use a set to avoid duplicates
    for request in accepted_friend_requests:
        # If current user is the sender, then the friend is the receiver, and vice versa
        friend = request.to_user if request.from_user == user else request.from_user
        if friend.pk in friends_ids:
            friends.add(friend)


    # Validation that non friends data was not requested
    friend_ids = {friend.pk for friend in friends}
    if not set(friends_ids).issubset(friend_ids):
        raise ValidationError("One or more of the provided friend IDs are not friends of the current user")

    
    # Find the best matching category for each friend
    best_matching_categories = {}
    friends_spending = {}
    friends_num_transactions = {}
    friends_avg_transactions = {}
    for friend in friends:
        friend_categories = Category.objects.filter(user=friend)
        category_scores = {}
        for friend_category in friend_categories:
            score = calculate_similarity(extract_keywords(friend_category.name), extract_keywords(category.name))
            category_scores[friend_category] = score
        # Sort the category scores in descending order
        sorted_scores = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
        chosen_category = sorted_scores[0][0]
        best_matching_categories[friend] = chosen_category

        # Calculate each friend's spending in the best matching category during the period
        friend_transactions = Transaction.objects.filter(user=friend, category=chosen_category, date__gte=start_date)
        friend_total = sum(transaction.amount for transaction in friend_transactions)
        friends_spending[friend.pk] = friend_total

        # Calculate the number of transactions and average transaction amount for each friend
        friend_num_transactions = len(friend_transactions)
        friend_avg_transaction = friend_total / friend_num_transactions if friend_transactions else 0
        friends_num_transactions[friend.pk] = friend_num_transactions
        friends_avg_transactions[friend.pk] = friend_avg_transaction

    # Get the transactions for all friends in the period
    all_friends_transactions = Transaction.objects.filter(user__in=friends, date__gte=start_date)

    # Filter the transactions based on the best matching categories
    friends_transactions = [
        transaction for transaction in all_friends_transactions.iterator() 
        if best_matching_categories[transaction.user] == transaction.category
    ]

    # Calculate the average spending of the friends in the best matching categories during the period
    friends_count = len(friends)
    friends_avg = sum(transaction.amount for transaction in friends_transactions) / friends_count if friends_transactions else 0

    # Calculate the difference between the user's spending and the friends' average spending
    difference = user_total - friends_avg

    return {
        'user_total': user_total,
        'user_num_transactions': user_num_transactions,
        'user_avg_transaction': user_avg_transaction,
        'friends_avg': friends_avg,
        'difference': difference,
        'friends_spending': friends_spending,
        'friends_num_transactions': friends_num_transactions,
        'friends_avg_transactions': friends_avg_transactions,
    }