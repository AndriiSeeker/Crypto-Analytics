document.addEventListener("DOMContentLoaded", function() {
  // Function to hide messages after a certain time (in milliseconds)
  function hideMessages() {
    var alertElements = document.querySelectorAll('.messages');
    alertElements.forEach(function(element) {
      element.style.display = 'none'; // Hide the alert messages
    });
  }

  // Call the hideMessages function after a certain delay (in milliseconds)
  setTimeout(hideMessages, 6000); // Messages will be hidden after 6 seconds (adjust the duration as needed)
});