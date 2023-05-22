$(document).ready(function() {
    $('.parent-row').click(function() {
      const transactionId = $(this).data('transaction-id');
      const childRows = $('.child-row[data-transaction-id="' + transactionId + '"]');
      childRows.toggle();
    });
  });
  