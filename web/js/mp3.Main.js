var M = null;

mp3.Main = function() {
    this.initLibrary();
    this.initPlaylist();
    this.initPlayer(); 
};

mp3.Main.extend(mp3.component.Object, {
    CLASSNAME: 'mp3.Main',
    
    initLibrary: function() {
        this.library = new mp3.view.Library('library');
        this.library.trackClicked.listen(function(a) {
            this.playlist.addFile(a);
        }.bind(this));
    },
    
    initPlaylist: function() {
        this.playlist = new mp3.view.Playlist('playlist');
        this.playlist.currentChanged.listen(function(engine) {
            this.player.engine = engine;
        }.bind(this));
    },
    
    initPlayer: function() {
        var titleScroller = new mp3.view.TitleScroller();    
        this.player = new mp3.view.Player('player', 'coverimg', titleScroller);
    }
});

mp3.hook(document, {
    DOMContentLoaded: function(e) {
        M = new mp3.Main();
    }
});
