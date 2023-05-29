from django.shortcuts import render
from django.db.models import Sum
from transactions.models import Transaction, Category
from .models import StickyNote, Board, BoardStickyNote
from budgets.models import CategoryBudget
from django.template import Context, Template
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

def analytics_view(request, board_id=None):
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

    # Retrieve the board using the board ID
    try:
        board = Board.objects.get(id=board_id)
        sticky_notes = board.sticky_notes.all()
    except Board.DoesNotExist:
        board = None
        sticky_notes = StickyNote.objects.all()

    # Render each sticky note template and store them in a dictionary
    rendered_sticky_notes = {}
    for sticky_note in sticky_notes:
        sticky_note_template = Template(sticky_note.content.html_content)
        context = Context({
            'id': sticky_note.id,  # Add the ID of the sticky note to the context
            'total_expenses': total_expenses,
            'monthly_expenses': monthly_expenses,
            'category_expenses': category_expenses,
            'total_income': total_income,
            'monthly_income': monthly_income,
            'budget_utilization': budget_utilization,
        })
        rendered_sticky_note_content = sticky_note_template.render(context)
        rendered_sticky_notes[sticky_note.title] = {
            'id': sticky_note.id,  # Include the ID in the rendered sticky note dictionary
            'content': rendered_sticky_note_content,  # Include the rendered content
        }

    context = {
        'board_id': board.pk,
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
def create_or_add_to_board(request):
    if request.method == 'POST':
        # Retrieve data from the POST request
        board_id = request.POST.get('board_id')
        board_name = request.POST.get('board_name')
        sticky_note_id = request.POST.get('sticky_note_id')
        position_x = request.POST.get('position_x')
        position_y = request.POST.get('position_y')
        user_id = request.POST.get('user_id')

        # Check if a board ID is provided
        if board_id:
            try:
                board = Board.objects.get(pk=board_id)
                sticky_note = StickyNote.objects.get(pk=sticky_note_id)

                # Add the sticky note to the existing board
                BoardStickyNote.objects.create(
                    board=board,
                    sticky_note=sticky_note,
                    position_x=position_x,
                    position_y=position_y,
                    user_id=user_id
                )

                # Return a success response
                response_data = {
                    'message': 'Sticky note added to the board successfully.',
                }
                return JsonResponse(response_data)

            except Board.DoesNotExist:
                return JsonResponse({'error': 'Board does not exist'}, status=404)
            except StickyNote.DoesNotExist:
                return JsonResponse({'error': 'Sticky note does not exist'}, status=404)

        else:
            # Create the Board instance
            board = Board.objects.create(name=board_name)

            # Create the BoardStickyNote instance
            sticky_note = StickyNote.objects.get(pk=sticky_note_id)
            BoardStickyNote.objects.create(
                board=board,
                sticky_note=sticky_note,
                position_x=position_x,
                position_y=position_y,
                user_id=user_id
            )

            # Return the board ID along with the success message
            response_data = {
                'message': 'Board and BoardStickyNote created successfully.',
                'board_id': board.id
            }
            return JsonResponse(response_data)

    return JsonResponse({'message': 'Invalid request method.'})



def fetch_board_sticky_notes(request, board_id):
    try:
        board = Board.objects.get(pk=board_id)
        board_sticky_notes = BoardStickyNote.objects.filter(board=board)
        data = []
        for board_sticky_note in board_sticky_notes:
            sticky_note = board_sticky_note.sticky_note
            data.append({
                'id': sticky_note.id,
                'title': sticky_note.title,
                'content': sticky_note.content.html_content,
                'position_x': board_sticky_note.position_x,
                'position_y': board_sticky_note.position_y
            })
        return JsonResponse(data, safe=False)
    except Board.DoesNotExist:
        return JsonResponse({'error': 'Board does not exist'}, status=404)
    

@csrf_exempt
def delete_sticky_note_from_board(request, board_id):
    if request.method == 'POST':
        # Retrieve data from the POST request
        sticky_note_id = request.POST.get('sticky_note_id')

        try:
            board = Board.objects.get(pk=board_id)
            sticky_note = StickyNote.objects.get(pk=sticky_note_id)

            # Remove the sticky note from the board
            board.sticky_notes.remove(sticky_note)

            # Return a success response
            response_data = {
                'message': 'Sticky note deleted from the board successfully.',
            }
            return JsonResponse(response_data)

        except Board.DoesNotExist:
            return JsonResponse({'error': 'Board does not exist'}, status=404)
        except StickyNote.DoesNotExist:
            return JsonResponse({'error': 'Sticky note does not exist'}, status=404)

    return JsonResponse({'message': 'Invalid request method.'})
