mp3.engine.Audio = function(id, target) {
    this.SUPER.call(this, id, target);
    this.audio = null;
    this.initialize();
};

/*
https://developer.mozilla.org/en/using_audio_and_video_in_firefox
http://dev.w3.org/html5/spec/video.html#audio
*/

mp3.engine.Audio.extend(mp3.engine.Base, {
    CLASSNAME: 'mp3.engine.Audio',
    
    _get_timeCurrent: function() { 
        return this.audio 
            ? this.audio.currentTime 
            : 0; 
    },
    
    _get_timeLoaded: function() {
        return this.audio 
            && this.audio.buffered 
            && this.audio.buffered.length
            ? this.audio.buffered.end(0)
            : 0;            
    },
    
    _get_timeTotal: function() { 
        return this.audio 
            ? this.audio.duration 
            : 0; 
    },
    
    _get_sizeLoaded: function() { 
        return 0; 
    },
    
    _get_sizeTotal: function() { 
        return 0; 
    },

    _get_volume: function() { 
        return this.audio 
            ? this.audio.volume 
            : 0; 
    },
    
    _set_volume: function(value) { 
        if (this.audio) {
            this.audio.volume = value; 
        }
    },
    
    initialize: function() {
        this.audio = document.createElement('audio');
        mp3.hook(this.audio, this.audioEvents, this);
        this.state = 'idle';
    },
    
    destroy: function() {
        mp3.unhook(this.audio, this.audioEvents);
        this.audio = null;
        this.state = 'ended';
    },
    
    load: function(url) {
        this.audio.src = url; 
        this.audio.load(); 
    },

    play: function() {
        this.audio.play();
    },

    pause: function() {
        this.audio.pause();
    },

    checkLoadFinish: function() {
        var freq = 1000/10;
        window.setTimeout(function(e) {
            this.timeChanged.notify();
            if (this.timeLoaded >= this.timeTotal) {
                this.log('{0} fullyLoaded'.format(this.id));
                this.fullyLoaded.notify();
            } else {
                window.setTimeout(arguments.callee.bind(this), freq);
            }
        }.bind(this), freq);
    },

    audioEvents: { 
        loadstart: function(e) { 
            this.state = 'loading'; 
            this.checkLoadFinish();
        },
        
        canplaythrough: function(e) { 
            this.state = 'ready'; 
        },
        
        play: function(e) { 
            this.state = 'playing'; 
        },
        
        ended: function(e) { 
            this.destroy();
        },

        durationchange: function(e) { 
            this.timeChanged.notify();
        },

        timeupdate: function(e) { 
            this.timeChanged.notify();
        },
        
        progress: function(e) {
            this.timeChanged.notify();
        },

        error: function(e) {  
            this.state = 'error'
            this.error(this.id + ' error!');
            this.dir(this.audio);
            this.destroy();
        }
    }
});
