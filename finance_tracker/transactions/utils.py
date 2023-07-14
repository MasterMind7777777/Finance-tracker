import re
from django.core.serializers.json import DjangoJSONEncoder
from django.forms import ValidationError
from .models import Category
from django.db.models import Max
from .models import Transaction, RecurringTransaction
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.cache import cache
from celery.result import AsyncResult
from .tasks import compare_spending_task, forecast_expenses_task
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

def forecast_expenses(user_id):
    # The key is 'forecast_expenses_task' + user_id
    cache_key = f'forecast_expenses_task_{user_id}'
    task_id = cache.get(cache_key)
    
    if task_id is None:
        # The task has not been launched yet, so we do it and store the task id in cache
        result = forecast_expenses_task.delay(user_id)
        cache.set(cache_key, str(result.id))
        return {"status": "Pending"}
    else:
        # A task has been launched in the past, we check its status
        result = AsyncResult(task_id)
        if result.ready():
            # If the task is ready, we clear the cache and return the result
            cache.delete(cache_key)
            return {"status": "Complete", "result": result.get()}
        else:
            return {"status": "Pending"}

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
    cache_key = f'compare_spending_task_{user_id}_{category_id}'
    task_id = cache.get(cache_key)
    
    if task_id is None:
        result = compare_spending_task.delay(user_id, friends_ids, category_id, period_days)
        cache.set(cache_key, str(result.id))
        return {"status": "Pending"}
    else:
        result = AsyncResult(task_id)
        if result.ready():
            if result.result['status'] == 'Pending':
                return {"status": "Pending"}
            elif result.result['status'] == 'Error':
                cache.delete(cache_key)
                raise ValidationError(result.result['message'])
            cache.delete(cache_key)
            return result.get()
        else:
            return {"status": "Pending"}