$(function() {
   $(".submission").click(function(event) {
       var challenge = $(event.target);
       var challenge_id = challenge.attr('id');

       var url = '/submission?challenge_id=' + challenge_id;
       $.get(url, function (data) {
            $('#detail_area').html(data);
       });
   });
});

$(function() {
   $(".waiting").click(function(event) {
       var url = '/waiting';
       $.get(url, function (data) {
            $('#detail_area').html(data);
       });
   });
});