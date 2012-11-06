mp3.view.Playlist = function(id) {
    this._currentIndex = 0;
    
    this.div = new mp3.component.VerticalScrollbar(id);
    this.currentChanged = new mp3.component.Observable();
    this.nextChanged = new mp3.component.Observable();
    
    this.items = [];
};

mp3.view.Playlist.extend(mp3.component.Object, {
    CLASSNAME: 'mp3.view.Playlist',
    
    _get_currentIndex: function() {
        return this._currentIndex;
    },
    
    _set_currentIndex: function(v) {
        this._currentIndex = v;
        this.currentChanged.notify(this.current);
    },

    _get_current: function() {
        return 0 <= this.currentIndex && this.currentIndex < this.items.length
            ? this.items[this.currentIndex]
            : null;
    },

    _get_next: function() {
        return 1 <= (this.currentIndex + 1) && (this.currentIndex + 1) < this.items.length
            ? this.items[this.currentIndex + 1]
            : null;
    },

    getFirst: function(states, cond) {
        for (var i = 0; i < this.items.length; i++) {
            if (!states.contains(this.items[i].engine.state)) {
                continue;
            }
            if (cond && !cond(this.items[i])) {
                continue;
            }
            return this.items[i];
        }
        return null;
    },
    
    addFile: function(a) {
        var a = mp3.template('playlistItemTemplate', 
                    {'url': a.href, 
                     'descr': a.innerText,
                     'id': 'item' + (this.div.content.childNodes.length + 1)}),
            item = new mp3.view.PlaylistItem(a);
            
        var currentWasEmpty = this.current == null;

        this.div.content.appendChild(a);
        this.items.push(item);

        item.engine.stateChanged.listen(this.loadNext.bind(this));
        item.engine.fullyLoaded.listen(this.loadNext.bind(this));
        
        this.div.resetHeight();

        if (currentWasEmpty) {
            this.current.isCurrent = true;
            this.currentChanged.notify(this.current);
        }
    },
        
    advance: function() {
        if (this.current) {
            this.current.isCurrent = false;
        }

        this.currentIndex += 1;

        if (this.current) {
            this.current.isCurrent = true;
        }
    },

    loadNext: function(item) {
        var firstLoading = this.getFirst(['loading', 'ready', 'playing'], function(item) { return item.engine.isLoading; });
        var firstIdle = this.getFirst(['idle']);

        if (firstLoading == null || !firstLoading.engine.isLoading) {
            if (firstIdle != null) {
                firstIdle.load();
            }
        }

        if (this.current && this.current.engine.state == 'ended') {
            this.advance();
        }

        if (this.current && this.current.engine.state == 'ready') {
            this.current.engine.play();
        }
    }
});
