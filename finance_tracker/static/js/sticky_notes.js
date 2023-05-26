$(function() {
    $(".draggable").draggable();
    $(".delete-note-btn").click(function() {
        $(this).closest(".sticky-note").remove();
    });

    // Fetch the sticky notes URL from the data attribute
    var fetchStickyNotesURL = $("#fetch-sticky-notes-url").data("url");

    // Fetch the sticky notes from the backend and populate the dropdown on page load
    $.ajax({
        url: fetchStickyNotesURL,
        type: 'GET',
        dataType: 'json',
        success: function(data) {
            // Process the returned sticky notes
            for (var i = 0; i < data.length; i++) {
                var stickyNote = data[i];
                // Create an option element for each sticky note
                var option = $('<option value="' + stickyNote.id + '">' + stickyNote.title + '</option>');
                // Append the option to the dropdown
                $("#sticky-note-dropdown").append(option);
            }
        },
        error: function(xhr, status, error) {
            console.error('Error fetching sticky notes:', error);
        }
    });

    $("#add-note-btn").click(function() {
        // Retrieve the selected sticky note's ID from the dropdown
        var selectedStickyNoteID = $("#sticky-note-dropdown").val();
        
        // Send a POST request to create the Board and BoardStickyNote
        $.ajax({
            url: 'analytics/create-board/',
            type: 'POST',
            data: {
                board_name: 'My Board',
                sticky_notes: [selectedStickyNoteID],
                positions_x: [0],  // Set the initial position as 0, you can change it according to your requirements
                positions_y: [0]
            },
            dataType: 'json',
            success: function(data) {
                console.log('Board and BoardStickyNote created successfully.');
                // Redirect to the analytics_view page with the selected sticky note ID as a parameter
                window.location.href = '/analytics/' + selectedStickyNoteID;
            },
            error: function(xhr, status, error) {
                console.error('Error creating Board and BoardStickyNote:', error);
            }
        });
    });
});
