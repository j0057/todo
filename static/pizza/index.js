(function($q, $qa, $hash) {
    document.addEventListener("DOMContentLoaded", function(e) {
        var slides = $qa(".slide");
        var slideCount = slides.length;
        var slideMaxState;
        var hash = {};

        var states = {
            1: function(slide, state) {
                $q("#title-pizza").className = state == 1 ? 'revealed' : "hidden";
            },
            3: function(slide, state) {
                $qa("dt", $qa(".slide")[slide]).map(function(dt, i) {
                    dt.style.display = i < state ? "block" : "none";
                });
                $qa("dd", $qa(".slide")[slide]).map(function(dd, i) {
                    dd.style.display = i < state ? "block" : "none";
                });
            },
            6: function(slide, state) {
                var popups = [4, 8, 12, 18, 21, 24, 27, 31, 34, 37, 40];
                $qa("img, g", $qa(".slide")[slide]).map(function(elem, i) {
                    var elemState = Number(elem.getAttribute("data-state"));
                    if (popups.indexOf(elemState) >= 0) {
                        elem.className = elemState == state ? "revealed" : "hidden";
                    }
                    else {
                        elem.style.display = elemState <= state ? "block" : "none";
                    }
                });
            }
        };

        var next = function() {
            if (hash.state < slideMaxState) {
                $hash.set({ slide: hash.slide, state: hash.state + 1 });
            }
            else if (hash.slide < (slides.length - 1)) {
                $hash.set({ slide: hash.slide + 1, state: 0 });
            }
        };
        var prev = function() {
            if (hash.state > 0) { 
                $hash.set({ slide: hash.slide, state: hash.state - 1 }); 
            }
            else if (hash.slide > 0) { 
                $hash.set({ slide: hash.slide - 1, state: 0 }); 
            }
        };

        var processHash = function(e) {
            var newHash = $hash.get();
            newHash.slide = Number(newHash.slide);
            newHash.state = Number(newHash.state);
            if (hash.slide != newHash.slide) {
                slides.map(function(slide) { slide.style.display = 'none'; });
                slides[newHash.slide].style.display = 'block';
                slideMaxState = Number(slides[newHash.slide].getAttribute("data-states"));
            };
            hash = newHash;
            if (states[hash.slide]) { 
                states[hash.slide](hash.slide, hash.state);
            }
        };

        window.addEventListener("keydown", function(e) {
            console && console.log && console.log(e, e.keyIdentifier, e.keyCode);
            switch (e.keyIdentifier) {
                case "Left":
                    prev();
                    break;
                case "Right":
                    next();
                    break;
            }
        });

        window.addEventListener("mousedown", function(e) {
            console && console.log && console.log(e, e.button);
            switch (e.button) {
                case 2:
                    //prev();
                    //e.preventDefault();
                    break;
                case 0:
                    next();
                    break;
            }
        });

        //window.addEventListener("contextmenu", function(e) { e.preventDefault(); });
        window.addEventListener("hashchange", processHash);

        if (!location.hash) { 
            $hash.set({ slide: 0, state: 0 });
        } else {
            processHash();
        }
});
})( function(s, ctx) {
        ctx = ctx || document;
        return ctx.querySelector(s);
    },
    function(s, ctx) {
        ctx = ctx || document;
        return Array.prototype.slice.call(ctx.querySelectorAll(s));
    },
    {
        get: function() {
            var result = {};
            location.hash
                .substr(1)
                .split("&")
                .map(function(kv) { return kv.split("=", 2); })
                .map(function(kv) { result[kv[0]] = decodeURI(kv[1]); });
            return result;
        },
        set: function(values) {
            var hash = "";
            for (var k in values) {
                if (hash) hash += "&";
                hash += k + "=" + encodeURI(values[k]);
            }
            location.hash = hash;
        }
    });
