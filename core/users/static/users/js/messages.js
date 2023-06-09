$(document).ready(function() {
    // Function to hide messages after a certain time (in milliseconds)
    function hideMessages() {
        $('.alert').fadeOut(500); // Fade out the alert messages over 0.5 seconds (adjust the duration as needed)
    }

    // Call the hideMessages function after a certain delay (in milliseconds)
    setTimeout(hideMessages, 3000); // Messages will be hidden after 3 seconds (adjust the duration as needed)
});