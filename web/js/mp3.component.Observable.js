mp3.component.Observable = function(sender) {
    this.listeners = [];
    this.sender = sender;
};

mp3.component.Observable.extend(mp3.component.Object, {
    CLASSNAME: 'mp3.component.Observable',
    
    listen: function(listener) {
        this.listeners.push(listener);
    },

    remove: function(listener) {
        var idx = this.listeners.indexOf(listener);
        this.listeners = this.listeners.slice(0, idx).concat(this.listeners.slice(idx + 1, this.listeners.length));
    },

    clear: function() {
        this.listeners = [];
    },

    notify: function(/*...*/) {
        var args = arguments;
        window.setTimeout(function(e) {
            this.listeners.map(function(listener) {
                listener.apply(this.sender, args);
            }.bind(this));
        }.bind(this), 1);
    }
});
