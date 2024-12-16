$(document).ready(function () {
  $("#reviewForm").submit(function (e) {
    e.preventDefault();
    $.ajax({
      data: $(this).serialize(),
      method: $(this).attr("method"),
      url: $(this).attr("action"),
      dataType: "json",
      success: function (response) {
        console.log("Saved");
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
          _html += ' <h4 class="user-name">' + response.context.user + "</h4>";
          _html += '<div class="star-rating">';
          for (let i = 1; i <= 5; i++) {
            if (i <= response.context.rating) {
              _html += '<span class="star">&#9733;</span>';
            } else {
              _html += '<span class="star empty">&#9733;</span> ';
            }
          }
          _html += " </div>";
          _html += '<div class="review-content">';
          _html += " <p>" + response.context.review + "</p>";
          _html += "</div>";
          _html += " </div>";
          _html += ' <div class="review-right">';
          _html +=
            ' <small class="review-time">' + response.context.date + "</small>";
          _html += " </div>";
          _html += " </div>";

          $(".reviews-list").prepend(_html);
        }
      },
      error: function (xhr, status, error) {
        console.log(xhr);
        console.log(status);
        console.log(error);
      },
    });
  });
});

$(document).ready(function () {
    $(".filter-checkbox,#price_filter_btn").on("click",()=>{
        console.log("clicked");
        let filter_object={}
        let min_price= $("#minamount").val()
        let max_price= $("#maxamount").val()
        filter_object.min_price=min_price;
        filter_object.max_price=max_price;
        $(".filter-checkbox").each(function(){
            let filter_value = $(this).val()
            let filter_key = $(this).data("filter")

            // console.log("filter value",filter_value);
            // console.log("filter key",filter_key);
            filter_object[filter_key]=Array.from(document.querySelectorAll('input[data-filter='+ filter_key + ']:checked')).map(function(element){
                return element.value
            })

            // console.log(filter_object);
            $.ajax({
                url:'/filter-product',
                data: filter_object,
                dataType: 'json',
                beforeSend: function(){
                    console.log('Sending data');
                },
                success:function(response) {

                    $("#filtered_products").html(response.data)
                },
                error:function(xhr,status,error){
                    console.log(xhr);
                    console.log(status);
                    console.log(error);
                }

            })
        })
    })
  })
