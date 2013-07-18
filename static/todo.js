$(function() {
    var render = function(targetID, templateID, data) {
        var template = $(templateID).html();
        var html = Mustache.render(template, data);
        $(targetID).html(html);
    };

    // load tasks
    $.get("/todo/tasks/")
        .done(function(data, response, xhr) {
            render("#tasks", "#tasks-template", data);
        })
        .fail(function(xhr, response, data) {
            alert(xhr.responseText);
        });

    // create new task
    $("#create-task").on("submit", function(e) {
        e.preventDefault();
        var form = $(e.target);
        $.ajax(form.attr("action"), 
               { "type": form.attr("method"), "data": form.serialize() })
            .done(function(_, _, xhr) {
                var loc = xhr.getResponseHeader("location");
                $.get(loc)
                    .done(function(content, response, xhr) {
                        window.location = window.location;
                    });
            })
            .fail(function(xhr, response, data) {
                alert(xhr.responseText);
            });
    });

    // update task
    $("#tasks").on("submit", ".task-edit", function(e) {
        e.preventDefault();
        var form = $(e.target);
        $.ajax(form.attr("action"), { type: form.attr("method"), data: form.serialize() })
            .done(function(data, response, xhr) {
                window.location = window.location;
            })
            .fail(function(xhr, response, data) {
                alert(xhr.responseText);
            });
    });
    
    // edit description
    $("#tasks").on("click", ".task-description", function(e) {
        var span = $(e.target);
        span.hide();
        span.parent()
            .find("input[name=\"description\"]")
            .attr("type", "text")
            .focus();
    });

    // edit is_done
    $("#tasks").on("click", "input[type=checkbox]", function(e) {
        e.preventDefault();
        var input = $(e.target);
        input.parent().submit();
    });

    // delete task
    $("#tasks").on("submit", "form.task-delete", function(e) {
        e.preventDefault();
        var form = $(e.target);
        $.ajax(form.attr("action"), { type: form.attr("method") })
            .done(function(content, response, xhr) {
                window.location = window.location;
            })
            .fail(function(xhr, response, data) {
                alert(xhr.responseText);
            }); 
    });
});
