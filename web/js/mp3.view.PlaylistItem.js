mp3.view.PlaylistItem = function(elem) {
    this.elem = elem;
    this.a = elem.getElementsByTagName('a')[0];
    this.url = this.a.href;
    this.status = elem.getElementsByClassName('status')[0];
    this.engine = new this.ENGINE_CLASS(elem.id, elem);
    this.engine.stateChanged.listen(this.updateStatus.bind(this));
    this.engine.timeChanged.listen(this.updateStatus.bind(this));
};

mp3.view.PlaylistItem.extend(mp3.component.Object, {
    CLASSNAME: 'mp3.view.PlaylistItem',
    ENGINE_CLASS: mp3.engine.Audio,

    _set_isCurrent: function(b) {
        this.elem.className = b ? 'current' : '';
    },
    
    load: function() {
        this.engine.load(this.a.href);
    },
    
    updateStatus: function() {
        this.status.innerText = this.engine.state;
        if ((this.engine.state == 'loading' || this.engine.state == 'ready' || this.engine.state == 'playing')
            && this.engine.timeLoaded < this.engine.timeTotal) {
            this.status.innerText += ' ({0}% loaded)'.format(
                Math.round(this.engine.timeLoaded / this.engine.timeTotal * 100));
        }
    }
});
