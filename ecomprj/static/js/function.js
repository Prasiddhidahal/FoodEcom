$(document).ready(function () {
  // Quantity increment/decrement
  $(".pro-qty").on("click", ".qtybtn", function () {
    var $button = $(this);
    var oldValue = $button.parent().find("input").val();
    var newVal = 1;

    if ($button.hasClass("inc")) {
      newVal = parseFloat(oldValue) + 1;
    } else {
      if (oldValue > 1) {
        newVal = parseFloat(oldValue) - 1;
      } else {
        newVal = 1;
      }
    }
    $button.parent().find("input").val(newVal);
  });

  // Image slider for the product images
  $(".product__details__pic__slider").owlCarousel({
    loop: true,
    margin: 10,
    nav: true,
    items: 4,
    autoplay: true,
    autoplayTimeout: 3000,
    autoplayHoverPause: true,
  });

  // Zoom image on click (optional)
  $(".product__details__pic__slider img").on("click", function () {
    var imgSrc = $(this).data("imgbigurl");
    $(".product__details__pic__item--large").attr("src", imgSrc);
  });

  // Handle review submission with AJAX
  $("#reviewForm").on("submit", function (e) {
    e.preventDefault(); // Prevent form from submitting traditionally

    var formData = $(this).serialize(); // Serialize the form data

    $.ajax({
      url: $(this).attr("action"), // The URL to submit to (your backend URL)
      type: "POST",
      data: formData,
      success: function (response) {
        // After successful submission, fetch updated reviews
        fetchReviews();
      },
      error: function (xhr, status, error) {
        console.error("Error submitting review:", error);
      },
    });
  });

  // Function to fetch updated reviews and update the review section
  function fetchReviews() {
    $.ajax({
      url: "/path-to-fetch-reviews/", // Replace with your actual endpoint
      type: "GET",
      success: function (data) {
        $("#reviewSection").html(data); // Update the reviews section with new data
      },
      error: function (xhr, status, error) {
        console.error("Error fetching reviews:", error);
      },
    });
  }
});
