$(document).ready(function() {
    $('.star-icon').click(function() {
        var coinId = $(this).data('coin-id');
        var csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
        var button = $(this); // Store a reference to the button element

        $.ajax({
            url: '/watchlist/',
            type: 'POST',
            data: {
                'coin_id': coinId,
                'csrfmiddlewaretoken': csrfToken
            },
            success: function(response) {
                if (response.status === 'added') {
                    // Update the star icon to colored state
                    button.addClass('colored');
                } else if (response.status === 'removed') {
                    // Update the star icon to uncolored state
                    button.removeClass('colored');
                }
            },
            error: function(xhr, status, error) {
                console.log(xhr.responseText);
            }
        });
    });
});
