/*global $, document, Chart, LINECHART, data, options, window, setTimeout*/
$(document).ready(function() {
  "use strict";

  // ---------------------------------------------- //
  // Preventing URL update on navigation link click
  // ---------------------------------------------- //
  $(".link-scroll").bind("click", function(e) {
    var anchor = $(this);
    $("html, body")
      .stop()
      .animate(
        {
          scrollTop: $(anchor.attr("href")).offset().top + 2
        },
        700
      );
    e.preventDefault();
  });

  // ---------------------------------------------- //
  // Search Bar
  // ---------------------------------------------- //
  $(".search-btn").on("click", function(e) {
    e.preventDefault();
    $(".search-area").fadeIn();
  });
  $(".search-area .close-btn").on("click", function() {
    $(".search-area").fadeOut();
  });
});
