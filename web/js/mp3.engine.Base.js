mp3.engine.Base = function(id, target) {
    this._state = 'initializing';
    this.id = id;
    this.target = target;
    this.stateChanged = new mp3.component.Observable();
    this.fullyLoaded = new mp3.component.Observable();
    this.timeChanged = new mp3.component.Observable();
    this.volumeChanged = new mp3.component.Observable();
};

mp3.engine.Base.extend(mp3.component.Object, {
    CLASSNAME: 'mp3.engine.Base',
    
    STATES: {
        'initializing': ['idle'],
        'idle': ['loading'],
        'loading': ['ready','error'],
        'ready': ['playing','error'],
        'playing': ['ended', 'paused', 'error'],
        'paused': ['playing'],
        'error': ['ended'],
        'ended': [] 
    },
    
    _get_isLoading: function() {
        return (this.state == 'loading')
            || (this.timeTotal > 0
                && this.timeLoaded < this.timeTotal);
    },
    
    _get_isLoaded: function() {
        return this.timeTotal > 0
            && this.timeLoaded == this.timeTotal;
    },

    _get_state: function() {
        return this._state;
    },

    _set_state: function(value) {
        if (mp3.keys(this.STATES).indexOf(value) == -1) {
            this.error('{0}: Illegal state \'{1}\''.format(this.id, value));
            return; 
        }
        if (this.state != null && this.STATES[this.state].indexOf(value) == -1) {
            this.error('{0}: Illegal state transition \'{1}\' to \'{2}\''.format(this.id, this.state, value));
            return;
        }
        this.log('{0} state {1} -> {2}'.format(this.id, this.state, value));
        this._state = value;
        this.stateChanged.notify(this, value);
    },

    load: function(url) {},
    play: function() {},
    pause: function() {},
    stop: function() {}
});
