$(document).ready(function() {
  // Handle delete transaction button click
  $(document).on('click', '.delete-transaction-btn', function() {
    var transactionId = $(this).data('transaction-id');

    // Show confirmation dialog
    if (confirm("Are you sure you want to delete this transaction?")) {
      // Send an AJAX request to delete the transaction
      $.ajax({
        type: "POST",
        url: '/transactions/' + transactionId + '/delete/', // Replace with your delete URL
        data: {
          csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
        },
        success: function(response) {
          // Handle the success response
          console.log(response);

          // Remove the deleted transaction row from the table
          $('button[data-transaction-id="' + transactionId + '"]').closest('tr').remove();
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
