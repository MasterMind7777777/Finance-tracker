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
        // console.log(response);

        // Update the transactions table with the new transaction
        var newRow = '<tr>' +
        '<td><button class="btn btn-danger delete-transaction-btn" data-transaction-id="' + response.id + '">Delete</button></td>' +
        '<td>' + response.date + '</td>' +
        '<td>' + response.title + '</td>' +
        '<td>' + response.description + '</td>' +
        '<td>' + response.amount + '</td>' +
        '<td>' + response.category + '</td>' +
        '</tr>';
      
      $('table.transactions-table tbody').append(newRow);
        // Reset the form
        $('#addTransactionForm')[0].reset();
      },
      error: function(xhr) {
        // Handle the error response
        console.log(xhr.responseText);
        // You can add code here to display an error message or handle specific error cases
      }
    });
  });
});
