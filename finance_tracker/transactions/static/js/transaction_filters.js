$(document).ready(function() {
    // Function to handle form submission and apply filters
    $('#transaction-filter-form').on('submit', function(event) {
        event.preventDefault(); // Prevent form submission

        // Get the form values
        var filter_by = $('#filter_by').val();
        var filter_value = '';

        if (filter_by === 'category') {
            filter_value = $('#category-filter').val();
        } else {
            filter_value = $('#filter_value').val();
        }

        // Modify filter value based on the field type
        if (filter_by === 'amount') {
            filter_value = parseFloat(filter_value);
        }

        // Create the AJAX request to fetch the filtered transactions
        $.ajax({
            url: $(this).attr('action'),
            type: $(this).attr('method'),
            data: {
                filter_by: filter_by,
                filter_value: filter_value
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

    // Function to handle the change event of the Filter By select
    $('#filter_by').on('change', function() {
        var filterBy = $(this).val();

        // Show/hide the filter value input and category dropdown based on the selected option
        if (filterBy === 'category') {
            $('#filter_value').hide();
            $('#category-filter').show();
            $('#filter_value_label').text('Category:');
        } else {
            $('#filter_value').show();
            $('#category-filter').hide();
            $('#filter_value_label').text('Filter Value:');
        }
    });
});
