(function($q, $qa) {
    document.addEventListener("DOMContentLoaded", function(e) {
        var state = 0;
        var states = [
            function() { $q("#slide-0").style.display = "block"; },
            function() { $q("#slide-1").style.display = "block"; },
            function() { $q("#slide-2").style.display = "block"; }
        ];

        var setState = function(newState) {
            $qa(".slide").map(function(slide) { slide.style.display = "none"; });
            states[state = newState]();
        };

        window.addEventListener("keydown", function(e) {
            if (e.keyIdentifier == "Left" && state > 0)
                setState(state - 1);
            else if (e.keyIdentifier == "Right" && state < (states.length - 1))
                setState(state + 1);
        });
});
})( function(s, ctx) {
        ctx = ctx || document;
        return ctx.querySelector(s);
    },
    function(s, ctx) {
        ctx = ctx || document;
        return Array.prototype.slice.call(ctx.querySelectorAll(s));
    });
