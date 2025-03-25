$(document).ready(function () {
  // Review Form Submission
  $("#reviewForm").submit(function (e) {
    e.preventDefault();
    $.ajax({
      data: $(this).serialize(),
      method: $(this).attr("method"),
      url: $(this).attr("action"),
      dataType: "json",
      success: function (response) {
        if (response.bool == true) {
          $("#review-res").html("Review Added Successfully.");
          $("#hide_review_form").hide();

          let _html = '<div class="review-item">';
          _html += '<div class="review-left">';
          _html +=
            '<img src="' +
            response.product +
            '" alt="' +
            response.context.user +
            '" class="user-photo">';
          _html += "</div>";
          _html += '<div class="review-middle">';
          _html += '<h4 class="user-name">' + response.context.user + "</h4>";
          _html += '<div class="star-rating">';
          for (let i = 1; i <= 5; i++) {
            _html +=
              i <= response.context.rating
                ? '<span class="star">&#9733;</span>'
                : '<span class="star empty">&#9733;</span>';
          }
          _html += "</div>";
          _html += '<div class="review-content">';
          _html += "<p>" + response.context.review + "</p>";
          _html += "</div></div>";
          _html += '<div class="review-right">';
          _html +=
            '<small class="review-time">' + response.context.date + "</small>";
          _html += "</div></div>";

          $(".reviews-list").prepend(_html);
        }
      },
      error: function (xhr, status, error) {
        console.log(xhr, status, error);
      },
    });
  });

  // Filter products by price and checkboxes
  $(".filter-checkbox,#price_filter_btn").on("click", function () {
    let filter_object = {
      min_price: $("#minamount").val(),
      max_price: $("#maxamount").val(),
    };
    $(".filter-checkbox").each(function () {
      let filter_key = $(this).data("filter");
      filter_object[filter_key] = Array.from(
        $("input[data-filter=" + filter_key + "]:checked")
      ).map((el) => el.value);
    });

    $.ajax({
      url: "/filter-product",
      data: filter_object,
      dataType: "json",
      beforeSend: function () {
        console.log("Sending data");
      },
      success: function (response) {
        $("#filtered_products").html(response.data);
      },
      error: function (xhr, status, error) {
        console.log(xhr, status, error);
      },
    });
  });

  // Price range validation
  $("#max_price").on("blur", function () {
    let min_price = parseFloat($(this).attr("min"));
    let max_price = parseFloat($(this).attr("max"));
    let current_price = parseFloat($(this).val());

    if (current_price < min_price || current_price > max_price) {
      alert("Price must be between $" + min_price + " and $" + max_price);
      $(this).val(min_price);
      $(this).focus();
    }
  });

  // Add to cart functionality
  $(document).on("click", ".add-to-cart", function (e) {
    e.preventDefault();
    let this_val = $(this);
    let index = this_val.attr("data-index");

    // Get selected color and size
    let color = $("input[name='color-choice-" + index + "']:checked").val();
    let size = $("input[name='size-choice-" + index + "']:checked").val();

    // Validate if color and size are selected
    if (!color) {
      alert("Please select a color.");
      return;
    }

    if (!size) {
      alert("Please select a size.");
      return;
    }

    let product_data = {
      id: $(".product-id-" + index).val(),
      title: $(".product-title-" + index).val(),
      price: $(".product-price-" + index).val(),
      qty: $(".product-quantity-" + index).val(),
      image: $(".product-image-" + index).val(),
      pid: $(".product-pid-" + index).val(),
      color: $(".product-color-" + index).val(),
      size: $(".product-size-" + index).val(),
    };

    $.ajax({
      url: "/add_to_cart/",
      method: "GET", // Consider switching to POST if necessary
      data: product_data,
      dataType: "json",
      beforeSend: function () {
        this_val.html("Adding to Cart...");
      },
      success: function (response) {
        $("#cart-item-count").text(response.totalcartitems);
        $("#cart-total-price").text("$" + response.cart_total_amount);
        this_val.html("✅");
      },
    });
  });


  // Remove from cart
  $(document).on("click", ".delete-product", function (e) {
    e.preventDefault();

    let product_id = $(this).attr("data-product");
    let this_val = $(this);
    console.log("Product ID:", product_id);

    $.ajax({
      url: "/remove_from_cart/", // Update this with your Django view URL
     
      data: {
        "id": product_id,
      },
      dataType: "json",
      beforeSend: function () {
        this_val.hide();
      },
      success: function (response) {
      this_val.show()
      $("#cart-item-count").text(response.totalcartitems);
      $("#cart-list").html(response.data);
      }
    });
  });

$(document).on("click", ".update-product", function (e) {
    e.preventDefault();

    let product_id = $(this).attr("data-product");
    let this_val = $(this);
    let product_quantity = $(".product-qty-"+ product_id).val();
    console.log("Product ID:", product_id);
    console.log("Product qty:", product_quantity);

$.ajax({
  url: "/update_from_cart/", // Update this with your Django view URL

  data: {
    "id": product_id,
    "qty": product_quantity,
  },
  dataType: "json",
  beforeSend: function () {
    this_val.hide();
  },
  success: function (response) {
    this_val.show();
    $("#cart-item-count").text(response.totalcartitems);
    $("#cart-list").html(response.data);
  },
});
    
  })

//make defult address
$(document).on("click", ".make-default-address", function (e) {
  e.preventDefault();

  let id = $(this).attr("data-address-id");
  let this_val = $(this);
  console.log("Address ID:", id);
  console.log("Element is:", this_val);

  $.ajax({
    url:"/make-default-address",
    data: {
      'id':id,
    },
    dataType:"json",
    success: function (response){
      console.log("Addresss made deafult");
      if (response.success==true) {
         $(".check").hide(), $(".action_btn").show(),
         $(".check"+id).show();
          $(".button" + id).hide();
         
      }
    }
  })

 

});

});
