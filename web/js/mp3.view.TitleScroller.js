mp3.view.TitleScroller = function() {
    this._title = '';
    this._offset = 0;
    this._direction = -1;
    
    window.setInterval(this.scroll.bind(this), 1000/2);
};

mp3.view.TitleScroller.extend(mp3.component.Object, {
    CLASSNAME: 'mp3.view.TitleScroller',
    
    _get_direction: function() { 
        return this._direction; 
    },
    
    _get_offset: function() { 
        return this._offset; 
    },
    
    _get_title: function() { 
        return this._title; 
    },
    
    _set_title: function(v) {
        this._title = v;
        this._offset = 0;
        this._direction = -1;
    },
    
    scroll: function() {
        if (this.title) {
            if (this.offset == this.title.length || this.offset == 0) {
                this._direction = -this.direction;
            }
            document.title = this.title.substr(this.offset);
            this._offset += this.direction;
        }
        else {
            document.title = 'mp3';
        }
    }
});
