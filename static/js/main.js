$(document).ready(function(){
   $(".method-link").click(function(){
       event.preventDefault();
       var method = $(this).data('method');
       var url = $(this).data('href');
       $.ajax({
           url: url,
           type: method,
           success: function(){
                location.reload();
           },
           error: function(){
               alert("Could not perform the selected action.");
           }
       });
   });

   var status = $(".model-status");
    if(status.length > 0){
        var getStatus = function(){
            $.ajax({
                url: $(status).data('href'),
                type: "GET",
                success: function(data){
                    $(status).html("Model creation status: " + data['task']['status'].toLowerCase() + ".  This message will auto-refresh until it is finished.");
                }
            });
        };
        window.setInterval(getStatus, 15000);
        getStatus();
    }
});