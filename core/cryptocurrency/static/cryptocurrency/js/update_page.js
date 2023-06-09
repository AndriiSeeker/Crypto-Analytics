  document.addEventListener('DOMContentLoaded', function() {
    // Function to reload the page
    function reloadPage() {
      console.log("Reloading the page..."); // Output a message in the console
      window.location.reload();
    }

    // Add event listener to the button
    document.querySelector('#update-rates-form button[type="submit"]').addEventListener('click', function(event) {
      event.preventDefault(); // Prevent the default form submission
      setTimeout(reloadPage, 7000);  // Delay of 7 seconds before reloading the page
      document.querySelector('#update-rates-form').submit(); // Manually submit the form
    });
  });