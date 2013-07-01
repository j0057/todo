function request(method, url, handler) {
    var xhr = new XMLHttpRequest();
    xhr.open(method, url, true);
    xhr.send();
    xhr.onreadystatechange = function() {
        if (xhr.readyState == xhr.DONE) {
            if (200 <= xhr.status && xhr.status < 300)
                handler(xhr);
            else
                alert(xhr.status + ": " + xhr.responseText);
        }
    }
}

document.addEventListener('DOMContentLoaded', function(e) {
    request('GET', '/oauth/session/check/', function(xhr) {
        document.querySelector('#session_id').textContent = document.cookie;
    });

    document.querySelector('#github_user').addEventListener('click', function(e) {
        e.preventDefault();
        request('GET', e.target.href, function(xhr) {
            var user = JSON.parse(xhr.response);
            document.querySelector('#github_user_result').innerHTML = "" 
                + "<img src=\"" + user.avatar_url + "\" title=\"" + user.login + "\"/>"
                ;
        });
    });

    document.querySelector('#github_following').addEventListener('click', function(e) {
        e.preventDefault();
        request('GET', e.target.href, function(xhr) {
            var following = JSON.parse(xhr.response);
            for (var i = 0; i < following.length; i++) {
                var user = following[i];
                document.querySelector('#github_following_result').innerHTML += ""
                    + "<img src=\"" + user.avatar_url + "\" title=\"" + user.login + "\" width=\"80\" height=\"80\"/>"
                    ;
            }
        });
    });

    document.querySelector('#github_followers').addEventListener('click', function(e) {
        e.preventDefault();
        request('GET', e.target.href, function(xhr) {
            var following = JSON.parse(xhr.response);
            for (var i = 0; i < following.length; i++) {
                var user = following[i];
                document.querySelector('#github_followers_result').innerHTML += ""
                    + "<img src=\"" + user.avatar_url + "\" title=\"" + user.login + "\" width=\"80\" height=\"80\"/>"
                    ;
            }
        });
    });

    document.querySelector('#facebook_me').addEventListener('click', function(e) {
        e.preventDefault();
        request('GET', e.target.href, function(xhr) {
            var me = JSON.parse(xhr.response);
            me.friends.data.map(function(user) {
                document.querySelector('#facebook_me_result').innerHTML += ''
                    + '<img src="https://graph.facebook.com/' + user.id + '/picture" title="' + user.name + '"/>'
                    ;
            })
        });
    });

    document.querySelector("#live_me").addEventListener("click", function(e) {
        e.preventDefault();
        request("GET", e.target.href, function(xhr) {
            var me = JSON.parse(xhr.response);
            document.querySelector("#live_me_result").textContent = me.name;
        });
    });
    
    document.querySelector("#google_userinfo").addEventListener("click", function(e) {
        e.preventDefault();
        request("GET", e.target.href, function(xhr) {
            var userinfo = JSON.parse(xhr.response);
            document.querySelector("#google_userinfo_result").textContent = userinfo.email;
        });
    });
});
