mp3.engine.Flash = function(id, target) {
    this.SUPER.call(this, id, target);
    this.flash = null;
    this.initialize();
};

// http://www.schillmania.com/projects/soundmanager2

mp3.engine.Flash.extend(mp3.engine.Base, {
    CLASSNAME: 'mp3.engine.Flash',
    
    _get_timeCurrent: function() { 
        return this.flash 
            ? this.flash.position / 1000.0 
            : 0; 
    },
    
    _get_timeLoaded: function() { 
        return this.flash 
            ? this.flash.duration / 1000.0 
            : 0; 
    },
    
    _get_timeTotal: function() { 
        return this.flash 
            ? this.flash.durationEstimate / 1000.0 
            : 0; 
    },
    
    _get_sizeLoaded: function() { 
        return this.flash 
            ? this.flash.bytesLoaded 
            : 0; 
    },
    
    _get_sizeTotal: function() { 
        return this.flash 
            ? this.flash.bytesTotal 
            : 0; 
    },

    _get_volume: function() { 
        return this.flash 
            ? this.flash.volume / 100.0 
            : 0; 
    },
    
    _set_volume: function(v) { 
        if (this.flash) 
            this.flash.setVolume(v * 100.0); 
    },

    _createStopwatch: function() {
        var time = function() { return (new Date()).getTime(); },
            now = time();
        return function() { return (time() - now) / 1000.0; };
    },
    
    load: function(url) { 
        this.stopwatch = this._createStopwatch();
        this.flash.url = url;
        this.flash.load();
    },

    play: function() { 
        this.flash.play();
    },

    pause: function() { 
        this.flash.pause();
    },

    stop: function() {
        this.flash.stop();
    },

    isReady: function() {
        var elapsed = this.stopwatch(),
            sizeRatio = this.sizeLoaded / this.sizeTotal,
            timeRatio = this.timeLoaded / this.timeTotal,
            estimateBySize = elapsed / sizeRatio,
            estimateByTime = elapsed / timeRatio;
        var result = (this.sizeTotal > (estimateBySize - elapsed))
                  && (this.timeTotal > (estimateByTime - elapsed));
        this.log('{0}: isReady elapsed={1} durationEstimate={2} estimateBySize={3} estimateByTime={4} : {5}'.format(
            this.id, elapsed, this.timeTotal, estimateBySize, estimateByTime, result?1:0));
        return result;
    },

    destroy: function() {
        this.flash.destroySound();
        this.flash = null;
    },
    
    initialize: function() { 
        if (this.flash) {
            this.flash.destroySound();
        }
        this.flash = soundManager.createSound({
            id: this.id + '-flash',
            
            whileloading: function(e) {
                if (this.state == 'idle')
                    this.state = 'loading';
                if (this.state == 'loading' && this.isReady())
                    this.state = 'ready';
                this.timeChanged.notify();
                this.sizeChanged.notify();
            }.bind(this),
            
            whileplaying: function(e) {
                if (this.state == 'ready')
                    this.state = 'playing';
                this.timeChanged.notify();
            }.bind(this),
            
            onjustbeforefinish: function(e) {
                if (this.state == 'playing') {
                    this.state = 'ended';
                    this.state = 'idle';
                }
            }.bind(this),
            
            onfinish: function(e) {
                if (this.state == 'playing') {
                    this.state = 'ended';
                    this.state = 'idle';
                }
            }.bind(this),
            
            onstop: function(e) {
                if (this.state == 'playing') {
                    this.state = 'ended';
                    this.state = 'idle';
                }
            }.bind(this),
            
            onbufferchange: function(e) {
                this.log('{0}: bufferchange {1}'.format(this.id, this.flash.isBuffering));
            }.bind(this)
        });
        this.state = 'idle';
    }
});

