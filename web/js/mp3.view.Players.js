mp3.view.Players = function(players, coverImg) {
    var titlescroller = new mp3.view.TitleScroller();
    this.currentIdx = 0;

    document.getElementById(players).appendChild(mp3.template('playerTemplate', {id:'player0'}));
    document.getElementById(players).appendChild(mp3.template('playerTemplate', {id:'player1'}));

    this.stateChanged = new mp3.component.Observable(this);
    this.players = [
        new mp3.view.Player('player0', coverImg, titlescroller),
        new mp3.view.Player('player1', coverImg, titlescroller)
    ];

    this.players.map(function(player) {
        player.stateChanged.listen(function(state) { 
            this.stateChanged.notify(player, state);
        }.bind(this));
    }.bind(this));
};

mp3.view.Players.extend(mp3.component.Object, {
    CLASSNAME: 'mp3.view.Players',
    
    _get_current: function() {
        return this.players[this.currentIdx];
    },
    
    _get_other: function() {
        return this.players[1 - this.currentIdx];
    },
    
    flip: function() {
        this.currentIdx = 1 - this.currentIdx;
    }
});
