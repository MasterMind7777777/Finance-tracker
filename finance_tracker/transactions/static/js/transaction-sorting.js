$(document).ready(function() {
    var currentSortField = '';  // Variable to store the current sort field
    var currentSortOrder = '';  // Variable to store the current sort order

    // Function to handle sorting when clicking on table headers
    $('.sortable').on('click', function() {
        var sortField = $(this).data('sort-field');
        var sortOrder = 'asc';  // Default sort order is ascending

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
    });
});
