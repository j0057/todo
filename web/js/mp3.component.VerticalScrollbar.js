mp3.component.VerticalScrollbar = function(id) {
    this._div = mp3.template('verticalScrollbarTemplate', {id:id});

    var old = document.getElementById(id);
    old.parentNode.replaceChild(this.div, old);

    this._value = 0.0;
    this._content = document.getElementById(id + '-content');
    this._scrollbar = document.getElementById(id + '-scrollbar');
    this._slider = document.getElementById(id + '-slider');
    
    var dragOffset = 0,
        dragEvents = {
            mousemove: function(e) {
                var mouseY = e.y - this.div.offsetTop - dragOffset,
                    vRange = this.div.offsetHeight - this.slider.offsetHeight,
                    ratio = mouseY / vRange;
                this.value = ratio;
            }.bind(this),
            
            mouseup: function(e) {
                this.log('mouseup {0} {1}'.format(e.x, e.y));
                mp3.unhook(window, dragEvents);
            }.bind(this)
        };

    mp3.hook(this.slider, {
        mousedown: function(e) {
            this.log('mousedown {0} {1} {2} {3}'.format(e.x, e.y, e.offsetX, e.offsetY));
            dragOffset = e.offsetY;
            mp3.hook(window, dragEvents);
            e.preventDefault();
        }.bind(this)
    });

    mp3.hook(this.div, {
        mousewheel: function(e) {
            var direction = e.wheelDeltaY < 0 ? 1 : -1,
                distance = Math.min(Math.abs(e.wheelDeltaY), 60),
                delta = direction * distance;
            this.value += delta / this.content.offsetHeight;
        }.bind(this) 
    });

    /** / 
    // BUG: doesn't end animation when clicking near end of scrollbar
    mp3.hook(this.scrollbar, {
        click: function(e) {
            var sb = this.scrollbar.getClientRects()[0],
                s = this.slider.getClientRects()[0];
            this.animate((e.y - sb.top) / (sb.height - s.height))
        }.bind(this)
    });
    /**/

    mp3.hook(window, {
        resize: this.resetHeight.bind(this)
    });
    
    this.resetHeight();
};

mp3.component.VerticalScrollbar.extend(mp3.component.Object, {
    CLASSNAME: 'mp3.component.VerticalScrollbar',
    
    _get_div: function() {
        return this._div; 
    },

    _get_content: function() {
        return this._content; 
    },

    _get_scrollbar: function() { 
        return this._scrollbar; 
    },

    _get_slider: function() {
         return this._slider; 
    },

    _get_value: function() { 
        return this._value; 
    },

    _set_value: function(v) {
        this._value = v < 0.0 ? 0.0 
                    : v > 1.0 ? 1.0 : v
        this.setSliderOffset(this._value);
        this.setContentOffset(this._value);
    },

    setSliderHeight: function() {
        var ratio = this.div.offsetHeight / this.content.offsetHeight;
        this.slider.style.height = "{0}%".format(ratio * 100);
    },

    setSliderOffset: function() {
        var range = this.scrollbar.offsetHeight - this.slider.offsetHeight;
        this.slider.style.marginTop = "{0}px".format(this.value * range); 
    },

    setContentOffset: function() {
        var range = this.content.offsetHeight - this.div.offsetHeight;
        this.content.style.marginTop = "{0}px".format(-this.value * range);
    },

    resetHeight: function() {
        this.setSliderHeight();
        var visible = this.div.offsetHeight / this.content.offsetHeight; // 0..1
        this.slider.style.display = (!visible || visible > 1.0) ? 'none' : 'block';
        this.value = -this.content.offsetTop / (this.content.offsetHeight - this.div.offsetHeight);
    },

    animate: function(targetValue) {
        var f = 1000/30, t = this;
        window.setTimeout(function(e) {
            var diff = targetValue - t.value,
                step = Math.min(diff / 10, 1);
            t.log(targetValue + ' ' + step + ' ' + Math.abs(diff))
            if (Math.abs(step * (t.scrollbar.offsetHeight - t.slider.offsetHeight)) >= 1) {
                t.value += step;
                window.setTimeout(arguments.callee, f);
            }
            else {
                console.log('done');
            }
        }, f);
    }
});
