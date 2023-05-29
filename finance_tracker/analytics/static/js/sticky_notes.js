$(function() {
    $(".draggable").draggable();
    
    $(".delete-note-btn").click(function() {
      var stickyNoteID = $(this).data("sticky-note-id");
      var boardID = $(this).data("board-id");
  
      // Send a POST request to delete the sticky note from the board
      $.ajax({
        url: "/analytics/delete-sticky-note/" + boardID + "/",
        type: "POST",
        data: {
            sticky_note_id: stickyNoteID,
        },
        dataType: "json",
        success: function(data) {
          console.log("Sticky note deleted from the board successfully.");
          // Remove the deleted sticky note element from the DOM
          $(this).closest(".sticky-note").remove();
          window.location.reload();
        },
        error: function(xhr, status, error) {
          console.error("Error deleting sticky note from the board:", error);
        },
      });
    });
  
    // Fetch the sticky notes URL from the data attribute
    var fetchStickyNotesURL = $("#fetch-sticky-notes-url").data("url");
  
    // Fetch the sticky notes from the backend and populate the dropdown on page load
    $.ajax({
      url: fetchStickyNotesURL,
      type: "GET",
      dataType: "json",
      success: function(data) {
        // Process the returned sticky notes
        for (var i = 0; i < data.length; i++) {
          var stickyNote = data[i];
          // Create an option element for each sticky note
          var option = $(
            '<option value="' +
              stickyNote.id +
              '">' +
              stickyNote.title +
              "</option>"
          );
          // Append the option to the dropdown
          $("#sticky-note-dropdown").append(option);
        }
      },
      error: function(xhr, status, error) {
        console.error("Error fetching sticky notes:", error);
      },
    });
  
    $("#add-note-btn").click(function() {
      // Retrieve the selected sticky note's ID from the dropdown
      var selectedStickyNoteID = $("#sticky-note-dropdown").val();
  
      // Retrieve the user ID from the data attribute
      var userID = $("#user-id").data("user-id");
  
      // Retrieve the current board ID from the URL
      var currentBoardID = getCurrentBoardIDFromURL();
  
      // If a board ID is found in the URL, add the sticky note to the existing board
      if (currentBoardID) {
        // Send a POST request to add the sticky note to the existing board
        $.ajax({
          url: "/analytics/create-or-add-to-board/",
          type: "POST",
          data: {
            board_id: currentBoardID,
            sticky_note_id: selectedStickyNoteID,
            position_x: 0,
            position_y: 0,
            user_id: userID,
          },
          dataType: "json",
          success: function(data) {
            console.log("Sticky note added to the board successfully.");
            // Redirect to the current board page
            window.location.reload();
          },
          error: function(xhr, status, error) {
            console.error("Error adding sticky note to the board:", error);
          },
        });
      } else {
        // Send a POST request to create a new board and add the sticky note
        $.ajax({
          url: "/analytics/create-or-add-to-board/",
          type: "POST",
          data: {
            board_name: "My Board",
            sticky_note_id: selectedStickyNoteID,
            position_x: 0,
            position_y: 0,
            user_id: userID,
          },
          dataType: "json",
          success: function(data) {
            console.log("Board and BoardStickyNote created successfully.");
            // Redirect to the analytics_view page with the board ID as a parameter
            window.location.href = "/analytics/" + data.board_id + "/";
          },
          error: function(xhr, status, error) {
            console.error("Error creating Board and BoardStickyNote:", error);
          },
        });
      }
    });
  
    // Function to retrieve the current board ID from the URL
    function getCurrentBoardIDFromURL() {
      var currentURL = window.location.href;
      var boardIDRegex = /analytics\/(\d+)\//;
      var matches = currentURL.match(boardIDRegex);
      if (matches && matches.length > 1) {
        return matches[1];
      }
      return null;
    }
  });
  