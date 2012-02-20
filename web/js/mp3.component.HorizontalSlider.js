mp3.component.HorizontalSlider = function(div, options) {
    this.changed = new mp3.component.Observable(this);
    
    this.div = mp3.template('horizontalSliderTemplate', {className:div.className, initText:options.text});
    this.slider = this.div.getElementsByClassName(div.className + '-slider')[0];
    
    div.parentNode.replaceChild(this.div, div);

    mp3.keys(options).map(function(k) { 
        this[k] = options[k];
    }.bind(this));
        
    var dragOffset = 0,
        dragEvents = {
            mousemove: function(e) {
                var div = this.div.getClientRects()[0],
                    slider = this.slider.getClientRects()[0];
                this.value = (e.x - div.left - dragOffset) / (div.width - slider.width);
            }.bind(this),
            mouseup: function(e) {
                mp3.unhook(window, dragEvents);
            }.bind(this)
        };

    mp3.hook(this.slider, {
        mousedown: function(e) {
            if (this.enabled) {
                dragOffset = e.offsetX;
                mp3.hook(window, dragEvents);
                e.preventDefault();
            }
        }.bind(this)
    });

};

mp3.component.HorizontalSlider.extend(mp3.component.Object, {
    CLASSNAME: 'mp3.component.HorizontalSlider',
    
    _get_value: function() { return this._value; },
    _set_value: function(x) {
        x = x < 0.0 ? 0.0 : x <= 1.0 ? x : 1.0;
        this._value = x;
        this.setSliderOffset(x);
        this.changed.notify(x);
    },
    
    _get_text: function() { return this.slider.innerText; },
    _set_text: function(v) { this.slider.innerText = v; },
    
    _get_enabled: function() { return this._enabled; },
    _set_enabled: function(v) { this._enabled = v; },

    setSliderOffset: function(x) {
        var div = this.div.getClientRects()[0],
            slider = this.slider.getClientRects()[0];
        this.slider.style.marginLeft = '{0}px'.format(x * (div.width - slider.width));
    }
});

