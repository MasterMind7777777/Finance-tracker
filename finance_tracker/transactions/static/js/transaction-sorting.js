$(document).ready(function() {
    var currentSortField = ''; // Variable to store the current sort field
    var currentSortOrder = ''; // Variable to store the current sort order
  
    // Define a variable to store the debounce timeout ID
    var debounceTimeout;
  
    // Function to handle sorting and filtering when clicking on table headers
    $('.sortable').on('click', function() {
      // Clear any existing debounce timeout
      clearTimeout(debounceTimeout);
  
      // Start a new debounce timeout
      debounceTimeout = setTimeout(function() {
        var sortField = $(this).data('sort-field');
        var sortOrder = 'asc'; // Default sort order is ascending
  
        // Toggle the sort order if the same field is clicked again
        if (currentSortField === sortField && currentSortOrder === 'asc') {
          sortOrder = 'desc';
        }
  
        currentSortField = sortField;
        currentSortOrder = sortOrder;
  
        // Update the data-sort-order attribute of all table headers
        $('.sortable').attr('data-sort-order', '');
  
        // Update the data-sort-order attribute of the clicked table header
        $(this).data('sort-order', sortOrder);
  
        // Create the AJAX request to fetch the sorted transactions
        $.ajax({
          url: $('#transaction-filter-form').attr('action'),
          type: $('#transaction-filter-form').attr('method'),
          data: {
            filter_by: $('#filter_by').val(),
            filter_value: $('#filter_value').val(),
            sort_field: currentSortField,
            sort_order: currentSortOrder
          },
          success: function(data) {
            // Update the transaction table body
            $('#transaction-table-body').html($(data).find('#transaction-table-body').html());
          },
          error: function(xhr, textStatus, errorThrown) {
            console.log('Error:', errorThrown);
          }
        });
      }, 300); // Set the debounce duration in milliseconds
    });
  });
  
  // Function to submit the transaction filter form
  function submitTransactionFilterForm() {
    var form = $('#transaction-filter-form');
  
    // Get the form action URL
    var actionUrl = form.attr('action');
  
    // Get the preserved filter values
    var filterBy = $('#filter_by').val();
    var filterValue = $('#filter_value').val();
  
    // Update the form action URL with the filter values
    var updatedActionUrl = updateUrlParameter(actionUrl, 'filter_by', filterBy);
    updatedActionUrl = updateUrlParameter(updatedActionUrl, 'filter_value', filterValue);
  
    // Set the updated action URL to the form
    form.attr('action', updatedActionUrl);
  
    // Submit the form
    form.submit();
  }
  
  // Function to update a URL parameter value
  function updateUrlParameter(url, param, value) {
    var urlParts = url.split('?');
    if (urlParts.length >= 2) {
      var baseUrl = urlParts[0];
      var params = urlParts[1].split('&');
  
      var updatedParams = [];
      var i;
      for (i = 0; i < params.length; i++) {
        var parameterName = params[i].split('=')[0];
        if (parameterName === param) {
          updatedParams.push(param + '=' + value);
        } else {
          updatedParams.push(params[i]);
        }
      }
  
      var updatedUrl = baseUrl + '?' + updatedParams.join('&');
      return updatedUrl;
    } else {
      return url;
    }
  }
  
  // Handle form submission for filtering
  $('#transaction-filter-form').on('submit', function(event) {
    event.preventDefault();
    submitTransactionFilterForm();
  });
  