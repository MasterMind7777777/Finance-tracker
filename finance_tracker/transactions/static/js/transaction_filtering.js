$(document).ready(function() {
    var currentSortField = ''; // Global variable to store the current sort field
    var currentSortOrder = ''; // Global variable to store the current sort order
  
    // Function to handle sorting when clicking on table headers
    $('.sortable').on('click', function() {
      var sortField = $(this).data('sort-field');
      var sortOrder = 'asc'; // Default sort order is ascending
  
      // Toggle the sort order if the same field is clicked again
      if (currentSortField === sortField && currentSortOrder === 'asc') {
        sortOrder = 'desc';
      }
  
      currentSortField = sortField;
      currentSortOrder = sortOrder;
  
      updateTable();
    });
  
    // Function to handle form submission for filtering
    $('#transaction-filter-form').on('submit', function(event) {
      event.preventDefault();
      updateTable();
    });
  
    // Function to update the transaction table with sorted and filtered data
    function updateTable() {
      var filterBy = $('#filter_by').val();
      var filterValue = $('#filter_value').val();
  
      // Create the AJAX request to fetch the sorted and filtered transactions
      $.ajax({
        url: $('#transaction-filter-form').attr('action'),
        type: $('#transaction-filter-form').attr('method'),
        data: {
          filter_by: filterBy,
          filter_value: filterValue,
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
    }
  });
  