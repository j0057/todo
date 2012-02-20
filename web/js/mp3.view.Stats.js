mp3.view.Stats = function(playerDiv, coverImg) {
    this.coverImg = coverImg;
    this.artistname = playerDiv.getElementsByClassName('artist-name')[0];
    this.albumname = playerDiv.getElementsByClassName('album-name')[0];
    this.trackname = playerDiv.getElementsByClassName('track-name')[0];
    this.playerstate = playerDiv.getElementsByClassName('player-state')[0];
};

mp3.view.Stats.extend(mp3.component.Object, {
    CLASSNAME: 'mp3.view.Stats',
    
    load: function(url) {
        this.httpRequest('GET', url.replace(/\.mp3$/, '.json'), function(xhr, json) {
            console.dir(this.coverImg);
            console.log(url);
            this.coverImg.src = json.cover ? url.replace(/\.mp3$/, '.jpg') : null;
            this.metadata = json;
            this.artistname.innerText = json.artist;
            this.albumname.innerText = json.album;
            this.trackname.innerText = json.track + '. ' + json.title;
        }.bind(this));
    },
});
