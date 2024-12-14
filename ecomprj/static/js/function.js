$("#commentForm").submit(function (e) {
  e.preventDefault(); // Prevent the default form submission

  // Check if the user is authenticated (optional check, handled by backend too)
  if (!isUserAuthenticated) {
    // Redirect to login or registration page if the user is not logged in
    window.location.href = "{% url 'userauth:login' %}";
    return;
  }

  $.ajax({
    data: $(this).serialize(), // Serialize the form data
    method: $(this).attr("method"), // Use the form's method (POST)
    url: $(this).attr("action"), // Use the form's action attribute (URL to send data to)
    success: function (response) {
      if (response.bool) {
        // Display the review and average rating
        $(".reviews-list").append(`
                    <div class="review-item">
                        <h6>${response.review.user}</h6>
                        <p>Rating: ${response.review.rating}</p>
                        <p>${response.review.review}</p>
                    </div>
                `);

        // Update the average rating
        $(".average-rating").text(
          `Average Rating: ${response.average_reviews}`
        );

        // Hide the form after successful submission
        $(".hide-comment-form").hide();

        console.log("Review submitted successfully");
      } else {
        alert(response.message); // Show error message
      }
    },
    error: function (xhr, status, error) {
      console.log("Error: " + error);
      alert("You cannot review this product more than once");
    },
  });
});
