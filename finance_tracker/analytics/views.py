from django.shortcuts import render
from django.db.models import Sum
from transactions.models import Transaction, Category
from .models import StickyNote, Board, BoardStickyNote
from budgets.models import CategoryBudget
from django.template import Context, Template
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

def analytics_view(request, sticky_note_id=None):
    # Expense Analytics
    total_expenses = Transaction.objects.filter(category__type='expense').aggregate(Sum('amount'))['amount__sum']
    monthly_expenses = Transaction.objects.filter(category__type='expense').values('date__year', 'date__month').annotate(total=Sum('amount'))
    category_expenses = Category.objects.filter(transaction__category__type='expense').annotate(total=Sum('transaction__amount'))

    # Income Analytics
    total_income = Transaction.objects.filter(category__type='income').aggregate(Sum('amount'))['amount__sum']
    monthly_income = Transaction.objects.filter(category__type='income').values('date__year', 'date__month').annotate(total=Sum('amount'))

    # Budget Analytics
    budget_utilization = CategoryBudget.objects.annotate(total_expenses=Sum('category__transaction__amount')).values('category__name', 'budget_limit', 'total_expenses')

    # Transaction Analysis
    transactions = Transaction.objects.all()

    if sticky_note_id is not None:
        sticky_notes = StickyNote.objects.filter(id=sticky_note_id)
    else:
        sticky_notes = StickyNote.objects.all()

    # Render each sticky note template and store them in a dictionary
    rendered_sticky_notes = {}
    for sticky_note in sticky_notes:
        sticky_note_template = Template(sticky_note.content.html_content)
        context = Context({
            'total_expenses': total_expenses,
            'monthly_expenses': monthly_expenses,
            'category_expenses': category_expenses,
            'total_income': total_income,
            'monthly_income': monthly_income,
            'budget_utilization': budget_utilization,
        })
        rendered_sticky_note_content = sticky_note_template.render(context)
        rendered_sticky_notes[sticky_note.title] = rendered_sticky_note_content

    context = {
        'transactions': transactions,
        'sticky_notes': rendered_sticky_notes,
    }

    return render(request, 'analytics/analytics.html', context)


def fetch_sticky_notes(request):
    sticky_notes = StickyNote.objects.all()
    data = []
    for sticky_note in sticky_notes:
        data.append({
            'id': sticky_note.id,
            'title': sticky_note.title,
            'content': sticky_note.content.html_content
        })
    return JsonResponse(data, safe=False)

@csrf_exempt  # Disable CSRF protection for simplicity. Use proper protection in production.
def create_board(request):
    if request.method == 'POST':
        # Retrieve data from the POST request
        board_name = request.POST.get('board_name')
        sticky_notes = request.POST.getlist('sticky_notes[]')
        positions_x = request.POST.getlist('positions_x[]')
        positions_y = request.POST.getlist('positions_y[]')
        user_id = request.POST.get('user_id')  # Retrieve the user ID from the request

        # Create the Board instance
        board = Board.objects.create(name=board_name)

        # Create the BoardStickyNote instances
        for i in range(len(sticky_notes)):
            sticky_note_id = sticky_notes[i]
            position_x = positions_x[i]
            position_y = positions_y[i]

            sticky_note = StickyNote.objects.get(pk=sticky_note_id)
            BoardStickyNote.objects.create(
                board=board,
                sticky_note=sticky_note,
                position_x=position_x,
                position_y=position_y,
                user_id=user_id
            )

        return JsonResponse({'message': 'Board and BoardStickyNotes created successfully.'})

    return JsonResponse({'message': 'Invalid request method.'})