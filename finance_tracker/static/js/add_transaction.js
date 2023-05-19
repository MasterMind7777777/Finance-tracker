$(document).ready(function() {
  // Initialize datetime picker
  $('#id_date').datetimepicker({
    format: 'YYYY-MM-DD HH:mm',
    icons: {
      time: 'far fa-clock',
      date: 'far fa-calendar',
      up: 'fas fa-chevron-up',
      down: 'fas fa-chevron-down',
      previous: 'fas fa-chevron-left',
      next: 'fas fa-chevron-right',
      today: 'far fa-calendar-check-o',
      clear: 'fas fa-trash',
      close: 'fas fa-times'
    }
  });

  // Show/hide the add transaction form
  $("#add-transaction-btn").click(function() {
    $("#add-transaction-form").toggle();
  });

  // Prevent form submission on enter key press
  $('.add-transaction-form').keydown(function(event) {
    if (event.keyCode == 13) {
      event.preventDefault();
      return false;
    }
  });

  // Handle form submission
  $(document).on('submit', '#addTransactionForm', function(event) {
    event.preventDefault();  // Prevent the default form submission

    // Serialize the form data
    var formData = $(this).serialize();

    // Send an AJAX request to the server
    $.ajax({
      type: "POST",
      url: $(this).attr("action"),
      data: formData,
      success: function(response) {
        // Handle the success response
        console.log(response);
        // You can add code here to update the transactions table or display a success message

        // Clear the form fields
        $('#id_title').val('');
        $('#id_description').val('');
        $('#id_amount').val('');
        $('#id_category').val('');
        $('#id_date').val('');

        // Append the new transaction to the table
        var transaction = response.transaction;
        var newRow = '<tr>' +
          '<td>' + transaction.title + '</td>' +
          '<td>' + transaction.description + '</td>' +
          '<td>' + transaction.amount + '</td>' +
          '<td>' + transaction.category + '</td>' +
          '<td>' + transaction.date + '</td>' +
          '<td><button class="btn btn-danger delete-transaction" data-transaction-id="' + transaction.id + '">Delete</button></td>' +
          '</tr>';
        $('table tbody').append(newRow);
      },
      error: function(xhr) {
        // Handle the error response
        console.log(xhr.responseText);
        // You can add code here to display an error message or handle specific error cases
      }
    });
  });

  // Handle transaction deletion
  $(document).on('click', '.delete-transaction', function() {
    var transactionId = $(this).data('transaction-id');
    if (confirm("Are you sure you want to delete this transaction?")) {
      $.ajax({
        type: "POST",
        url: '/transactions/' + transactionId + '/delete/',
        success: function(response) {
          // Handle the success response
          console.log(response);
          // You can add code here to update the transactions table or display a success message
          $(this).closest('tr').remove(); // Remove the deleted transaction row
        },
        error: function(xhr) {
          // Handle the error response
          console.log(xhr.responseText);
          // You can add code here to display an error message or handle specific error cases
        }
      });
    }
  });
});
