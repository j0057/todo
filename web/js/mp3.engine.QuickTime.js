mp3.engine.QuickTime = function(id, target) {
    this.SUPER.call(this, id, target);
    this.qtDiv = null;
    this.qt = null;
}

mp3.engine.QuickTime.extend(mp3.engine.Base, {
    CLASSNAME: 'mp3.engine.QuickTime',
    
    _get_timeCurrent: function() { 
        return this.qt 
            ? this.qt.GetTime() / 1000.0 
            : 0; 
    },
    
    _get_timeLoaded: function() { 
        return this.qt 
            ? this.qt.GetMaxTimeLoaded() / 1000.0 
            : 0; 
    },
    
    _get_timeTotal: function() { 
        return this.qt 
            ? this.qt.GetDuration() / 1000.0 
            : 0; 
    },
    
    _get_sizeLoaded: function() { 
        return this.qt 
            ? this.qt.GetMaxBytesLoaded() 
            : 0; 
    },
    
    _get_sizeTotal: function() { 
        return this.qt 
            ? this.qt.GetMovieSize() 
            : 0; 
    },

    _get_volume: function() { 
        return this.qt 
            ? this.qt.GetVolume() 
            : 0; 
    },
    
    _set_volume: function(v) { 
        if (this.qt) 
            this.qt.SetVolume(v); 
    },

    isReady: function() {
        var elapsed = ((new Date()).getTime() - this.t1) / 1000,
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

    load: function(url) { 
        this.qtDiv = mp3.template('quickTimeTemplate', {id:this.id+'-qt', url:url});
        this.target.appendChild(this.qtDiv);
        this.qt = document.getElementById(this.id + '-qt-object');

        mp3.hook(this.qtObject, {
            qt_progress: function(e) {
                if (this.state == 'idle')
                    this.state = 'loading';
                if (this.state == 'loading' && this.isReady())
                    this.state = 'ready';
            }.bind(this),
            
            qt_canplaythrough: function(e) {
                this.state = 'ready';
            }.bind(this),
            
            qt_play: function(e) {
                this.state = 'playing';
            }.bind(this),
            
            qt_ended: function(e) {
                this.state = 'ended';
                this.state = 'initializing';
                this.state = 'idle';
            }.bind(this),
            
            qt_durationchange: function(e) {
                this.timeChanged.notify();
            }.bind(this),
            
            qt_timechanged: function(e) {
                this.timeChanged.notify();
            }.bind(this)
        });
        
        this.state = 'loading';
    },

    play: function() { 
        this.qt.Play();
    },

    pause: function() { 
        this.qt.Stop();
    },

    stop: function() {
    },
});

