$(document).ready(function() {
    var currentSortField = '';  // Variable to store the current sort field
    var currentSortOrder = '';  // Variable to store the current sort order

    // Function to handle form submission and apply filters/sorting
    $('#transaction-filter-form').on('submit', function(event) {
        event.preventDefault(); // Prevent form submission

        // Get the form values
        var filter_by = $('#filter_by').val();
        var filter_value = $('#filter_value').val();

        // Create the AJAX request to fetch the filtered and sorted transactions
        $.ajax({
            url: $(this).attr('action'),
            type: $(this).attr('method'),
            data: {
                filter_by: filter_by,
                filter_value: filter_value,
                sort_field: currentSortField,
                sort_order: currentSortOrder
            },
            success: function(data) {
                // Get the transaction list from the returned HTML
                var transactionList = $(data).find('.table-responsive').html();
            
                // Update only the transaction list
                $('.table-responsive').html(transactionList);
            },
            error: function(xhr, textStatus, errorThrown) {
                console.log('Error:', errorThrown);
            }
        });
    });

    // Function to handle sorting when clicking on table headers using event delegation
    $(document).on('click', '.sortable', function() {
        var sortField = $(this).data('sort-field');

        // Toggle the sort order if the same field is clicked
        if (sortField === currentSortField) {
            currentSortOrder = (currentSortOrder === 'asc') ? 'desc' : 'asc';
        } else {
            currentSortField = sortField;
            currentSortOrder = 'asc';
        }

        // Trigger form submission to apply sorting
        $('#transaction-filter-form').submit();
    });
});
