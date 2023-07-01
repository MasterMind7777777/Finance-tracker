from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from transactions.models import Transaction, Category
from .models import StickyNote, Board, BoardStickyNote
from budgets.models import CategoryBudget
from django.template import Context, Template
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

def analytics_view(request, board_id=None):
    try:
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

        main_board = False
        # Retrieve the board using the board ID
        if board_id:
            board = get_object_or_404(Board, id=board_id)
            board_sticky_notes = board.boardstickynote_set.all()
        else:
            board = get_object_or_404(Board, id=41)
            board_sticky_notes = board.boardstickynote_set.all()
            main_board = True

        # Render each sticky note template and store them in a dictionary
        rendered_sticky_notes = {}
        for board_sticky_note in board_sticky_notes:
            sticky_note = board_sticky_note.sticky_note
            sticky_note_template = Template(sticky_note.content.html_content)
            context = Context({
                'id': sticky_note.id,
                'total_expenses': total_expenses,
                'monthly_expenses': monthly_expenses,
                'category_expenses': category_expenses,
                'total_income': total_income,
                'monthly_income': monthly_income,
                'budget_utilization': budget_utilization,
                'given_title': board_sticky_note.given_title,
            })
            rendered_sticky_note_content = sticky_note_template.render(context)
            rendered_sticky_notes[sticky_note.title + ": " + str(board_sticky_note.given_title)] = {
                'id': sticky_note.id,
                'content': rendered_sticky_note_content,
                'given_title': board_sticky_note.given_title,
                'position_x': board_sticky_note.position_x,
                'position_y': board_sticky_note.position_y,
            }

        context = {
            'board_id': board_id,
            'transactions': transactions,
            'sticky_notes': rendered_sticky_notes,
            'main_board': main_board
        }

        return render(request, 'analytics/analytics.html', context)

    except Exception as e:
        # Handle unexpected exceptions
        error_message = str(e)
        return render(request, 'error.html', {'error_message': error_message})


def fetch_sticky_notes(request):
    try:
        sticky_notes = StickyNote.objects.all()
        data = []
        for sticky_note in sticky_notes:
            data.append({
                'id': sticky_note.id,
                'title': sticky_note.title,
                'content': sticky_note.content.html_content
            })
        return JsonResponse(data, safe=False)

    except Exception as e:
        # Handle unexpected exceptions
        response_data = {
            'error': str(e)
        }
        return JsonResponse(response_data, status=500)


@csrf_exempt  # Disable CSRF protection for simplicity. Use proper protection in production.
def create_or_add_to_board(request):
    try:
        if request.method == 'POST':
            # Retrieve data from the POST request
            board_id = request.POST.get('board_id')
            board_name = request.POST.get('board_name')
            sticky_note_id = request.POST.get('sticky_note_id')
            position_x = request.POST.get('position_x')
            position_y = request.POST.get('position_y')
            user_id = request.POST.get('user_id')
            given_title = request.POST.get('given_title')

            # Check if a board ID is provided
            if board_id:
                board = get_object_or_404(Board, pk=board_id)
                sticky_note = get_object_or_404(StickyNote, pk=sticky_note_id)

                # Add the sticky note to the existing board
                BoardStickyNote.objects.create(
                    board=board,
                    sticky_note=sticky_note,
                    position_x=position_x,
                    position_y=position_y,
                    user_id=user_id,
                    given_title=given_title
                )

                # Return a success response
                response_data = {
                    'message': 'Sticky note added to the board successfully.',
                }
                return JsonResponse(response_data)

            else:
                # Create the Board instance
                board = Board.objects.create(name=board_name)

                # Create the BoardStickyNote instance
                sticky_note = get_object_or_404(StickyNote, pk=sticky_note_id)
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

    except Exception as e:
        # Handle unexpected exceptions
        response_data = {
            'error': str(e)
        }
        return JsonResponse(response_data, status=500)


def fetch_board_sticky_notes(request, board_id):
    try:
        board = get_object_or_404(Board, pk=board_id)
        board_sticky_notes = board.boardstickynote_set.all()
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

    except Exception as e:
        # Handle unexpected exceptions
        response_data = {
            'error': str(e)
        }
        return JsonResponse(response_data, status=500)


@csrf_exempt
def delete_sticky_note_from_board(request, board_id):
    try:
        if request.method == 'POST':
            # Retrieve data from the POST request
            given_title = request.POST.get('given_title')

            board = get_object_or_404(Board, pk=board_id)
            sticky_note = board.sticky_notes.filter(boardstickynote__given_title=given_title).first()

            if sticky_note:
                board_sticky_note = BoardStickyNote.objects.filter(board=board, sticky_note=sticky_note, given_title=given_title).first()

                if board_sticky_note:
                    # Delete the BoardStickyNote entry
                    board_sticky_note.delete()

                    # Return a success response
                    response_data = {
                        'message': 'Sticky note deleted from the board successfully.',
                    }
                    return JsonResponse(response_data)
                else:
                    return JsonResponse({'error': 'Sticky note does not exist in the board'}, status=404)
            else:
                return JsonResponse({'error': 'Sticky note does not exist'}, status=404)

        return JsonResponse({'message': 'Invalid request method.'})

    except Exception as e:
        # Handle unexpected exceptions
        response_data = {
            'error': str(e)
        }
        return JsonResponse(response_data, status=500)


@csrf_exempt
def save_board(request):
    try:
        if request.method == 'POST':
            # Retrieve data from the POST request
            board_name = request.POST.get('board_name')
            sticky_notes_data = request.POST.get('sticky_notes')

            # Get or create the board
            board, created = Board.objects.get_or_create(name=board_name)

            # Process sticky notes data
            sticky_notes = json.loads(sticky_notes_data)
            for sticky_note_data in sticky_notes:
                sticky_note_id = sticky_note_data['sticky_note_id']
                position_x = sticky_note_data['position_x']
                position_y = sticky_note_data['position_y']
                user_id = sticky_note_data['user_id']
                given_title = sticky_note_data['given_title']

                # Retrieve the StickyNote object
                sticky_note = get_object_or_404(StickyNote, pk=sticky_note_id)

                # Add the sticky note to the board with positions
                BoardStickyNote.objects.create(
                    board=board,
                    sticky_note=sticky_note,
                    position_x=position_x,
                    position_y=position_y,
                    user_id=user_id,
                    given_title=given_title
                )

            # Return a success message
            response_data = {
                'message': 'Board saved successfully.',
                'board_id': board.id,
                'created': created
            }
            return JsonResponse(response_data)

        else:
            # Return an error message for unsupported request method
            response_data = {
                'error': 'Invalid request method. Only POST method is supported.'
            }
            return JsonResponse(response_data, status=400)

    except Exception as e:
        # Handle unexpected exceptions
        response_data = {
            'error': str(e)
        }
        return JsonResponse(response_data, status=500)


def fetch_user_boards(request, user_id):
    try:
        # Retrieve boards that belong to the user
        boards = Board.objects.filter(boardstickynote__user_id=user_id).distinct()

        # Create a list of board data
        data = []
        for board in boards:
            data.append({
                'id': board.id,
                'name': board.name,
                'sticky_notes_count': board.sticky_notes.count()
            })

        # Return the data as JSON response
        return JsonResponse(data, safe=False)

    except Exception as e:
        # Handle unexpected exceptions
        response_data = {
            'error': str(e)
        }
        return JsonResponse(response_data, status=500)
