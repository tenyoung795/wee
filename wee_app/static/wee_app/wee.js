jQuery(document).ready(function($) {
    $(".clickable-tr").click(function() {
        window.document.location = $(this).data("href");
    });
});
