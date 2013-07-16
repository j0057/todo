$(function() {
    $("#login button").click(function(e) {
        e.preventDefault();
        $.post("/todo/login/", $("#login").serialize())
            .done(function() {
                window.location  = "/todo/todo.xhtml";
            })
            .fail(function(xhr) { 
                alert(xhr.responseText); 
            });
    });

    $("#signup button").click(function(e) {
        e.preventDefault();
        $.post("/todo/signup/", $("#signup").serialize())
            .done(function() {
                window.location  = "/todo/login.xhtml";
            })
            .fail(function(xhr) { 
                alert(xhr.responseText); 
            });
    });
});
