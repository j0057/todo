mp3.view.Library = function(id) {
    this.div = new mp3.component.VerticalScrollbar(id);
    
    this.artistClicked = new mp3.component.Observable(this.div.content);
    this.albumClicked = new mp3.component.Observable(this.div.content);
    this.trackClicked = new mp3.component.Observable(this.div.content);

    if (this.LAZY) {
        mp3.hook(this.div.content, this.divEventsLazy, this);
        this.loadArtistsLazy();
    }
    else {
        mp3.hook(this.div.content, this.divEventsEager, this);
        this.httpRequest('GET', 'mp3.json?lazy=false', function(xhr, json) {
            this.updateArtistsEager(json);
        }.bind(this));
    }
};

mp3.view.Library.extend(mp3.component.Object, {
    CLASSNAME: 'mp3.view.Library',
    ARROW_RIGHT: '\u25B6', // '►',
    ARROW_DOWN:  '\u25BC', // '▼',
    LAZY: true,
    
    info: {},
    
    loadArtistsLazy: function() {
        this.httpRequest('GET', 'mp3.json?lazy=true', function(xhr, json) {
            // instantiate artist templates
            json.map(function(artist) {
                    return mp3.template('libraryArtistTemplate', {artist: artist});
                })
                .map(this.div.content.appendChild.bind(this.div.content));
            
            // cache result
            json.map(function(artist) { 
                this.info[artist] = {}; 
            }.bind(this));

            // reset height of div
            this.div.resetHeight();
        }.bind(this));
    },
    
    loadAlbumsLazy: function(artist, artistName) {
        // get list of albums for artist
        this.httpRequest('GET', mp3.urlJoin('mp3', artistName + '.json?lazy=true'), function(xhr, json) {
            // instantiate album template
            json.map(function(albumName) {
                    return mp3.template('libraryAlbumTemplate', {
                        album: albumName, 
                        url: mp3.urlJoin('mp3', artistName, albumName) + '.zip',
                        visibility: 'visible'});
                })
                .map(artist.appendChild.bind(artist));
            
            // cache result
            json.map(function(albumName) { 
                this.info[artistName][albumName] = {}; 
            }.bind(this));
        }.bind(this));
    },
    
    loadTracksLazy: function(album, artistName, albumName) {
        // get tracks for album
        this.httpRequest('GET', mp3.urlJoin('mp3', artistName, albumName) + '.json', function(xhr, json) {
            // instantiate track template
            mp3.keys(json)
                .sorted()
                .map(function(trackNum) {
                    return mp3.template('libraryTrackTemplate', {
                        trackNum:trackNum, 
                        trackName:json[trackNum], 
                        url:mp3.urlJoin('mp3', artistName, albumName, trackNum, json[trackNum]) + '.mp3',
                        visibility:'visible'
                    });
                })
                .map(album.appendChild.bind(album));
            
            // cache result
            mp3.keys(json)
                .map(function(trackNum) {
                    this.info[artistName][albumName][trackNum] = json[trackNum];
                }.bind(this));
        }.bind(this));
    },
    
    divEventsLazy: {
        click: function(e) {
            e.preventDefault();

            var classes = e.target.className.split(' ');

            // handle click on arrow
            if (classes.contains('arrow')) {
                // the parent will be an artist or an album
                var item = e.target.parentNode;
                console && console.dirxml && console.dirxml(item);
                
                // load albums if not in cache
                if (item.className.split(' ').contains('artist')) {
                    var artistName = item.getElementsByClassName('artist-name')[0].textContent;
                    if (!mp3.keys(this.info[artistName]).length) {
                        this.loadAlbumsLazy(item, artistName);
                    }
                }
                
                // load tracks if not in cache
                else if (item.className.split(' ').contains('album')) {
                    var albumName = item.getElementsByClassName('album-name')[0].textContent,
                        artistName = item.parentNode.getElementsByClassName('artist-name')[0].textContent;
                    if (!mp3.keys(this.info[artistName][albumName]).length) {
                        this.loadTracksLazy(item, artistName, albumName);
                    }
                }
                
                // reset height of div
                this.div.resetHeight();
            }
            else if (classes.contains('artist-name')) {
                this.artistClicked.notify(e.target);
            }
            else if (classes.contains('album-name')) {
                this.albumClicked.notify(e.target);
            }
            else if (classes.contains('track-name')) {
                this.trackClicked.notify(e.target);
            }
        }
    },

    updateEager: function(json) {
        var arrowRight = this.arrowRight;
        mp3.keys(json)
            .sorted()
            .map(function(artist) {
                var artistDiv = mp3.template('libraryArtistTemplate', {artist:artist});
                mp3.keys(json[artist])
                    .sorted()
                    .map(function(album) {
                        var albumDiv = mp3.template('libraryAlbumTemplate', {
                                artist:artist, 
                                album:album, 
                                zip:mp3.urlJoin('mp3', '{0}/{1}.zip'.format(artist, album)),
                                visibility: 'collapsed'});
                        mp3.keys(json[artist][album])
                            .sorted()
                            .map(function(trackNum) {
                                return mp3.template('libraryTrackTemplate', {
                                    trackNum:trackNum, 
                                    trackName:json[artist][album][trackNum],
                                    mp3:mp3.urlJoin('mp3', artist, album, trackNum, json[artist][album][trackNum] + '.mp3'),
                                    visibility:'collapsed'})
                            })
                            .map(albumDiv.appendChild.bind(albumDiv));
                        return albumDiv;
                    })
                    .map(artistDiv.appendChild.bind(artistDiv));
                return artistDiv;
            })
            .map(this.div.content.appendChild.bind(this.div.content));
        
        this.div.resetHeight();
    },

    divEventsEager: {
        click: function(e) {
            e.preventDefault();
            if (e.target.className.split(' ').contains('arrow')) {
                var div = e.target.nextSibling.nextSibling;
                while (div) {
                    if (div.className) {
                        if (div.className.split(' ').contains('collapsed'))
                            div.className = div.className.replace('collapsed', 'visible');
                        else
                            div.className = div.className.replace('visible', 'collapsed');
                    }
                    div = div.nextSibling;
                }
                e.target.innerText = (e.target.innerText == this.arrowDown)
                    ? this.arrowRight 
                    : this.arrowDown;
            }
            else if (e.target.className.split(' ').indexOf("track-name") > -1) {
                this.itemClicked.notify(e.target);
            }
            else if (e.target.className.split(' ').indexOf('album-name') > -1) {
                this.itemClicked.notify(e.target);
            }
            else if (e.target.className.split(' ').indexOf('artist-name') > -1) {
                this.itemClicked.notify(e.target);
            }
            this.div.resetHeight();
        }
    }
});
