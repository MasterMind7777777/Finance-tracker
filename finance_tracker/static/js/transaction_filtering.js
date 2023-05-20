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
  
    // Event listener for the change event of the "Filter By" field
    $('#filter_by').on('change', function() {
      var filterBy = $(this).val();
  
      // Check if the filterBy field is set to 'Category'
      if (filterBy === 'Category') {
        $('#filter_value').hide();
        $('#category-filter').show();
      } else {
        $('#filter_value').show();
        $('#category-filter').hide();
      }
    });
  
    // Function to update the transaction table with sorted and filtered data
    function updateTable() {
        var filterBy = $('#filter_by').val();
        var filterValue = $('#filter_value').val();
    
        // Check if the filterBy field is set to 'Category'
        if (filterBy === 'Category') {
        filterValue = $('#category-filter').val();
        }
    
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
          
            // Update the dropdown options if the filterBy field is set to 'Category'
            if (filterBy === 'Category') {
              var categoryOptions = '';
              $(data).find('#category-filter option').each(function() {
                categoryOptions += '<option value="' + $(this).val() + '">' + $(this).text() + '</option>';
              });
              $('#category-filter').html(categoryOptions);
            }
        },
        error: function(xhr, textStatus, errorThrown) {
            console.log('Error:', errorThrown);
        }
        });
    }
  });
  