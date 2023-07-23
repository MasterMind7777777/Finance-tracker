import csv
from decimal import Decimal
import io
from celery import chain, chord, group, shared_task
from datetime import date, timezone
import calendar
from django.db.models import Sum, Q, Max
import re

from django.http import JsonResponse
from users.models import FriendRequest
from transactions.models import Transaction, Category, RecurringTransaction
from django.contrib.auth import get_user_model
from django.core.cache import cache
from datetime import datetime, timedelta
from celery.result import AsyncResult
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


User = get_user_model()

@shared_task(bind=True)
def forecast_expenses_task(self, user_id):
    user = User.objects.get(pk=user_id)  # get the user instance from user_id

    today = date.today()
    start_of_month = today.replace(day=1)

    # Calculate the total number of days in the month
    total_days_in_month = calendar.monthrange(today.year , today.month)[1]

    # Calculate the actual number of days that have passed in the current month
    days_passed = (today - start_of_month).days + 1

    print('days_passed task')
    print(days_passed)

    expenses = Transaction.objects.filter(user=user, date__gte=start_of_month).aggregate(total_expenses=Sum('amount'))
    total_expenses = expenses['total_expenses'] or 0


    # Calculate the average daily expenses
    avg_daily_expenses = total_expenses / days_passed

    # Calculate the forecasted expenses for the remaining days of the month
    forecast_next_month = avg_daily_expenses * total_days_in_month

    return forecast_next_month

@shared_task
def compare_spending_task(user_id, friends_ids, category_id, period_days=30):
    user = User.objects.get(pk=user_id)
    try:
        category = Category.objects.get(pk=category_id, user=user)
    except Category.DoesNotExist:
        return {
            'status': 'Error',
            'message': f"{category_id} is not one of categories of current user."
        }

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
        return {
            'status': 'Error',
            'message': "One or more of the provided friend IDs are not friends of the current user"
        }

    
    # Find the best matching category for each friend
    best_matching_categories = {}
    friends_spending = {}
    friends_num_transactions = {}
    friends_avg_transactions = {}

    # Get the task IDs from the cache
    cache_key = "friend_task_ids"
    friend_task_ids = cache.get(cache_key)

    if not friend_task_ids:
        friend_task_ids = []  # Store the task IDs for all the tasks
        for friend in friends:
            friend_data_task = process_friend_data_task.delay(friend.pk, category.name, start_date, period_days)
            # Store the task IDs
            friend_task_ids.append(friend_data_task.id)
        # Cache the list of friend task IDs
        cache.set(cache_key, friend_task_ids)

    # Initialize a dictionary to store the task results
    task_results = {}

    # Check each task
    for task_id in friend_task_ids:
        result = AsyncResult(task_id)
        # If the task is not ready, return "Pending" status
        if not result.ready():
            return {
                'status': 'Pending'
            }
        elif result.ready(): # If the task is ready, but subtasks are pending
            output = result.result
            print(output)
            if output['status'] == 'Pending':
                return {
                    'status': 'Pending'
                }
            else:
                task_results[output['result']['friend_id']] = output

    cache.delete(cache_key)

    # Get the transactions for all friends in the period
    all_friends_transactions = Transaction.objects.filter(user__in=friends, date__gte=start_date)
    friends_count = len(friend_ids)

    # Filter the transactions based on the best matching categories
    for transaction in all_friends_transactions.iterator():
        if task_results[transaction.user.pk]['result']['best_matching_category'] == transaction.category.id:
            if transaction.user.pk in friends_spending:
                friends_spending[transaction.user.pk] += transaction.amount
                friends_num_transactions[str(transaction.user.pk)] += 1
            else:
                friends_spending[transaction.user.pk] = transaction.amount
                friends_num_transactions[str(transaction.user.pk)] = 1

    # Calculate the total spending and total count across all friends
    total_spending = sum(friends_spending.values())

        # Calculate the average transaction amount for each friend
    for friend_id, total in friends_spending.items():
        count = friends_num_transactions[str(friend_id)]
        friends_avg_transactions[str(friend_id)] = Decimal(total) / Decimal(count) if count > 0 else 0

    # Calculate the average spending of the friends in the best matching categories during the period
    friends_avg = total_spending / friends_count if friends_count > 0 else 0

    # Calculate the difference between the user's spending and the average spending of friends
    difference = user_total - friends_avg


    spending_comparison = {
        'status': 'Complete',
        'result': {
            'user_total': user_total,
            'user_num_transactions': user_num_transactions,
            'user_avg_transaction': user_avg_transaction,
            'friends_avg': friends_avg,
            'difference': difference,
            'friends_spending': friends_spending,
            'friends_num_transactions': friends_num_transactions,
            'friends_avg_transactions': friends_avg_transactions,
        }
    }

    return spending_comparison

@shared_task
def process_friend_data_task(friend_id, category_name, start_date, period_days):
    friend = User.objects.get(pk=friend_id)
    friend_categories = Category.objects.filter(user=friend)
    category_scores = {}
    # Fetch the tasks results for each friend
    cache_key = f"task_ids_calculate_category_similarity_task_{friend_id}"
    task_ids = cache.get(cache_key)

    if not task_ids:
        task_ids = []
        for friend_category in friend_categories:
            similarity_task = calculate_category_similarity_task.delay(friend_category.name, friend_category.pk, category_name)
            # Store the task IDs
            task_ids.append(similarity_task.id)
        cache.set(f"task_ids_calculate_category_similarity_task_{friend_id}", task_ids)

    calculate_category_results = []
    for task_id in task_ids:
        result = AsyncResult(task_id)
        if not result.ready():
            return {
                'status': 'Pending'
            }
        else:
            result_status = check_calculate_category_similarity_task(task_id)
            result_status = check_calculate_category_similarity_task(task_id) #FIXME
            print(result_status)
            if result_status['status'] == 'Pending':
                return {
                    'status': 'Pending'
                }
            else:
                calculate_category_results.append(result_status['result'])
    
    cache.delete(cache_key)

    for task_result in calculate_category_results:
        category_scores[task_result.get('friend_category')] = task_result.get('score')
        
    # Sort the category scores in descending order
    sorted_scores = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
    chosen_category = sorted_scores[0][0]
    
    # Calculate each friend's spending in the best matching category during the period
    friend_transactions = Transaction.objects.filter(user=friend, category=chosen_category, date__gte=start_date)
    friend_total = sum(transaction.amount for transaction in friend_transactions)
    
    # Calculate the number of transactions and average transaction amount for each friend
    friend_num_transactions = len(friend_transactions)
    friend_avg_transaction = friend_total / friend_num_transactions if friend_transactions else 0

    return {
        'status': 'Complete',
        'result':{
            'friend_id': friend_id,
            'best_matching_category': chosen_category,
            'spending': friend_total,
            'num_transactions': friend_num_transactions,
            'avg_transaction': friend_avg_transaction
        }
    }

@shared_task(bind=True)
def calculate_category_similarity_task(self, friend_category_name, friend_category_id, category_name):
    # Schedule the two extract_keywords_tasks
    task1 = extract_keywords_task.delay(friend_category_name)
    task2 = extract_keywords_task.delay(category_name)

    # Store the task IDs in the cache
    cache.set(f"{self.request.id}_subtask1_id", task1.id)
    cache.set(f"{self.request.id}_subtask2_id", task2.id)

    return {"status": "Pending", "friend_category": friend_category_id}

def check_calculate_category_similarity_task(task_id):
    # Get the task IDs from the cache
    subtask1_id = cache.get(f"{task_id}_subtask1_id")
    subtask2_id = cache.get(f"{task_id}_subtask2_id")

    # Check if both subtasks are ready
    if AsyncResult(subtask1_id).ready() and AsyncResult(subtask2_id).ready():
        # Get the results of the subtasks
        keywords1 = AsyncResult(subtask1_id).result['keywords']
        keywords2 = AsyncResult(subtask2_id).result['keywords']
    else:
        return {"status": "Pending"}

    # Check if calculate_similarity_task is already in progress
    cache_key = f"{task_id}_similarity_task_id"
    similarity_task_id = cache.get(cache_key)
    if similarity_task_id is not None:
        similarity_task = AsyncResult(similarity_task_id)
        if similarity_task.ready():
            similarity = similarity_task.result
            # Clean up the cache
            cache.delete(f"{task_id}_subtask1_id")
            cache.delete(f"{task_id}_subtask2_id")
            result = AsyncResult(task_id).result
            cache.delete(cache_key)
            return {
                "status": "Complete", 
                "result": {
                    "score": similarity,
                    "friend_category": result['friend_category']
                }
            }
        else:
            return {"status": "Pending"}
    else:
        # Perform calculate_similarity_task
        similarity_task = calculate_similarity_task.delay(keywords1, keywords2)

        # Store the task ID in the cache
        cache.set(cache_key, similarity_task.id)

        return {"status": "Pending"}

@shared_task(bind=True)
def categorize_transaction_task(self, transaction_id, user_id):
    # Define a cache key for this task

    # The task hasn't been initiated yet, proceed with the task
    uncategorized_transaction = Transaction.objects.get(id=transaction_id)

    text = uncategorized_transaction.title + ' ' + uncategorized_transaction.description

    # Create a chain of tasks starting with find_matching_category_task
    task_chain = find_matching_category_task.s(text, user_id, transaction_id)
    task_chain_result = task_chain.apply_async()

    # Save the task data to the cache
    return {"status": "Pending"}


@shared_task(bind=True)
def find_matching_category_task(self, text, user_id, transaction_id):
    categories = Category.objects.filter(user=user_id)

    original_text_keywords_task = extract_keywords_task(text)
    keyword_tasks = []
    for category in categories:
        related_transactions = Transaction.objects.filter(category=category)
        for transaction in related_transactions:
            keyword_tasks.append(
                extract_keywords_task.s(transaction.title + ' ' + transaction.description, category.id)
            )

    callback_subtask = calculate_similarity_task_chain.s(original_text_keywords_task['keywords']) | on_all_tasks_done.s(transaction_id)
    task_chain = chord(keyword_tasks, callback_subtask)
    task_chain_result = task_chain.apply_async()

    cache_key = f"categorize_transaction_task_{transaction_id}_{user_id}"
    cache.set(cache_key, task_chain_result.id)

    return {"status": "Pending", "job_id": task_chain_result.id}

@shared_task
def extract_keywords_task(text, category_id=None):
    cleaned_text = re.sub(r'[^a-zA-Z0-9\s]', '', text.lower())

    # Tokenize the cleaned text into individual words
    words = word_tokenize(cleaned_text)

    # Remove common stop words
    stop_words = set(stopwords.words('english'))
    keywords = [word for word in words if word not in stop_words]
    return {"keywords": keywords, "category_id": category_id}

@shared_task(bind=True)
def calculate_similarity_task(self, keywords1, keywords2, ):
    set1 = set(keywords1)
    set2 = set(keywords2)
    intersection = set1.intersection(set2)
    union = set1.union(set2)
    similarity = len(intersection) / len(union)
    return similarity

@shared_task(bind=True)
def calculate_similarity_task_chain(self, results, original_text_keywords):
    similarities = {}
    for res in results:
        keywords1 = original_text_keywords
        keywords2 = res['keywords']
        category_id = res['category_id']
        set1 = set(keywords1)
        set2 = set(keywords2)
        intersection = set1.intersection(set2)
        union = set1.union(set2)
        similarity = len(intersection) / len(union)
        similarities[category_id] = similarity
    output = {'status': 'Complete', 'result': similarities, }
    return output

@shared_task
def on_all_tasks_done(results, transaction_id):
    # Find the result with the highest similarity
    highest_similarity_result = max(results['result'].items(), key=lambda x: x[1])
    output = {"status": "Complete", "best_matching_category": highest_similarity_result[0]}
    return output

@shared_task
def apply_recurring_transactions_task(frequency):
    current_date = timezone.now().date()

    latest_transaction_dates = Transaction.objects.filter(
        recurring_transaction__isnull=False,
        recurring_transaction__frequency=frequency,
        date__date__lt=current_date
    ).values('recurring_transaction').annotate(latest_date=Max('date__date'))

    recurring_transactions = RecurringTransaction.objects.filter(
        pk__in=[item['recurring_transaction'] for item in latest_transaction_dates]
    )

    transactions_to_create = []

    for transaction_date in latest_transaction_dates:
        recurring_transaction = next(
            rt for rt in recurring_transactions if rt.pk == transaction_date['recurring_transaction']
        )
        latest_date = transaction_date['latest_date']

        if recurring_transaction.frequency == frequency and (current_date - latest_date).days >= 1:
            transactions_to_create.append(
                Transaction(
                user=recurring_transaction.user,
                title=f'Recurring Transaction {recurring_transaction.id}',
                amount=recurring_transaction.amount,
                category=recurring_transaction.category,
                date=timezone.now(),
                recurring_transaction=recurring_transaction))

    Transaction.objects.bulk_create(transactions_to_create)

@shared_task
def process_transactions_chunk(transactions):
    # Process a chunk of transactions
    try:
        Transaction.objects.bulk_create(transactions)
        return {'status': 'Complete'}
    except Exception as e:
        return {'status': 'Error', 'message': f'Error: {e}'}


@shared_task
def prepare_transactions_chunks(file_content, user_id):
    try:
        file_wrapper = io.StringIO(file_content)
        reader = csv.DictReader(file_wrapper)
        transactions = []
        category_ids = set()

        chunks = []
        chunk_size = 100

        for index, row in enumerate(reader):
            category_id = row['category_id']
            category_ids.add(category_id)

            transaction = Transaction(
                user_id=user_id,
                category_id=category_id,
                title=row['title'],
                description=row['description'],
                amount=row['amount'],
                date=row['date']
            )
            transactions.append(transaction)

            if index % chunk_size == 0 and index > 0:
                chunks.append(process_transactions_chunk.si(transactions))
                transactions = []

        # Last chunk
        if transactions:
            chunks.append(process_transactions_chunk.si(transactions))

        categories_exist = Category.objects.filter(id__in=category_ids).values_list('id', flat=True)

        # Convert category_ids to a set of integers
        category_ids = set(map(int, category_ids))

        # Perform the comparison
        if set(categories_exist) != category_ids:
            return {'status': 'Error', 'message': 'Invalid category IDs.'}

        chord(chunks)(finalize_transactions_upload.s(user_id))

    except Exception as e:
        # Handle the exception here
        print({'status': 'Error', 'message': f'Error occurred: {str(e)}'})
        return {'status': 'Error', 'message': f'Error occurred: {str(e)}'}

    return {'status': 'Error', 'message': 'No file uploaded.'}


@shared_task(bind=True)
def finalize_transactions_upload(self, result, user_id):
    task_id = self.request.id
    # Fetch the updated transactions from the database
    cache.set(f'bulk_upload_status_{user_id}', task_id)
    return {'status': 'Complete', 'message': 'Transactions uploaded successfully.'}