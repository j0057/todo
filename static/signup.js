$(function() {
    $("#signup").submit(function(e) {
        e.preventDefault();
        var $form = $(e.target);
        $.post($form.attr("action"), $form.serialize())
            .done(function() {
                window.location = "/todo/login.xhtml";
            })
            .fail(function(xhr) { 
                alert(xhr.responseText); 
            });
    });
});
