mp3.view.Player = function(div, coverImg, titlescroller) {
    this._engine = null;

    this.div = document.getElementById(div);
    this.id = this.div.id;
    this.coverImg = document.getElementById(coverImg);

    this.div.appendChild(mp3.template('playerTemplate', {id: 'player0'}));
    this.titlescroller = titlescroller;

    this.stats = new mp3.view.Stats(this.div, this.coverImg);
    
    this.time = new mp3.component.HorizontalSlider(
        this.div.getElementsByClassName('time')[0], 
        {value: 0.0, enabled: false, text: '0/0'});
    
    this.volume = new mp3.component.HorizontalSlider(
        this.div.getElementsByClassName('volume')[0], 
        {value: 1.0, enabled: true, text: '11'});

    this.volume.changed.listen(function(x, y) {
        if (this.engine) {
            this.engine.volume = Math.pow(this.volume.value, 3);
        }
        this.volume.text = Math.round(x * 11);
    }.bind(this));
};

mp3.view.Player.extend(mp3.component.Object, {
    CLASSNAME: 'mp3.view.Player',
    
    _get_engine: function() {
        return this._engine; 
    },
    
    _set_engine: function(playlistItem) {
        if (this.engine) {
            // HACK: should call remove method but have no good way to remember stored .bound method
            // FIX: .notify should return an index
            this.engine.timeChanged.listeners = [];
        }

        this._engine = playlistItem ? playlistItem.engine : null;

        if (this.engine) {
            this.engine.timeChanged.listen(this.setTime.bind(this));
            this.stats.load(playlistItem.url);
        }
    },

    setTime: function() {
        this.time.value = this.engine.timeCurrent / this.engine.timeTotal;
        this.time.text = Math.round(this.engine.timeCurrent) + '/' + Math.round(this.engine.timeTotal);
    },
    
    play: function() {
        this.coverImg.src = this.stats.coverImage;
        with (this.stats.metadata) {
            this.titlescroller.title = '{0} - {1} - {2} - {3}'.format(artist, album, track, title);
        }
    },
});
