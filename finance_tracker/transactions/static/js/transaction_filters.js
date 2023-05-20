$(document).ready(function() {
    var currentSortField = '';  // Variable to store the current sort field
    var currentSortOrder = '';  // Variable to store the current sort order

    // Fetch categories and populate the dropdown field
    $.ajax({
        url: '/categories/',
        type: 'GET',
        success: function(data) {
            var categories = data.categories;
            var categorySelect = $('#filter_by');

            // Clear previous options
            categorySelect.empty();

            // Add a default option
            categorySelect.append($('<option>').text('None').val(''));

            // Add options for each category
            categories.forEach(function(category) {
                categorySelect.append($('<option>').text(category.name).val(category.name));
            });
        },
        error: function(xhr, textStatus, errorThrown) {
            console.log('Error:', errorThrown);
        }
    });

    // Function to handle form submission and apply filters/sorting
    $('#transaction-filter-form').on('submit', function(event) {
        event.preventDefault(); // Prevent form submission

        // Get the form values
        var filterBy = $('#filter_by').val();
        var filterValue = $('#filter_value').val();
        var filterDate = $('#filter_date').val();

        // Modify filter value based on the field type
        if (filterBy === 'amount') {
            filterValue = parseFloat(filterValue);
        } else if (filterBy === 'date') {
            // Convert the filter value to a valid date format
            var filterDateObj = new Date(filterDate);
            var year = filterDateObj.getFullYear();
            var month = (filterDateObj.getMonth() + 1).toString().padStart(2, '0');
            var day = filterDateObj.getDate().toString().padStart(2, '0');
            filterDate = year + '-' + month + '-' + day;
        }

        // Create the AJAX request to fetch the filtered and sorted transactions
        $.ajax({
            url: $(this).attr('action'),
            type: $(this).attr('method'),
            data: {
                filter_by: filterBy,
                filter_value: filterValue,
                filter_date: filterDate,
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

    // Function to handle sorting when clicking on table headers using event delegation
    $(document).on('click', '.sortable', function() {
        var clickedSortField = $(this).data('sort-field');
        var clickedSortOrder = 'asc';

        // Check if the clicked field is the same as the current sort field
        if (clickedSortField === currentSortField) {
            // Reverse the sort order if it's the same field
            clickedSortOrder = (currentSortOrder === 'asc') ? 'desc' : 'asc';
        }

        // Update the current sort field and sort order
        currentSortField = clickedSortField;
        currentSortOrder = clickedSortOrder;

        // Trigger form submission to apply sorting
        $('#transaction-filter-form').submit();
    });
});
