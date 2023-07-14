from django.utils import timezone
from .models import FinancialHealth
from api_v1.serializers import FinancialHealthSerializer
from .tasks import create_financial_health_task

def check_financial_health(user_id):
    # Check if financial health was generated in the past 30 minutes
    check = was_financial_health_generated_recently(user_id)
    exist = check[0]
    financial_health = check[1]
    if exist:
        # Output the result
        return output_financial_health_result(financial_health)
    else:
        # Create a task to generate the financial health
        create_financial_health_task(user_id)
        return {'status': 'Pending'}

def was_financial_health_generated_recently(user_id):
    last_generation_time = retrieve_last_generation_time(user_id)
    time = last_generation_time[0]
    financial_health = last_generation_time[1]

    if time is not None:
        # Make both datetimes offset-aware by attaching the timezone information
        current_time = timezone.now()
        time = time.replace(tzinfo=timezone.get_current_timezone())

        time_difference = current_time - time
        time_difference_minutes = time_difference.total_seconds() / 60

        return [(time_difference_minutes <= 30), financial_health] 

    return [False, None]

def retrieve_last_generation_time(user_id):
    # Retrieve the timestamp of the most recent financial health generation for the user from the database
    financial_health = FinancialHealth.objects.filter(user_id=user_id).order_by('-id').first()
    if financial_health:
        return [financial_health.created_at, financial_health]
    else:
        return [None, None]

def output_financial_health_result(financial_health):
    serializer = FinancialHealthSerializer(financial_health)
    return {'status': 'Complete', 'financial_health_result': serializer.data}
