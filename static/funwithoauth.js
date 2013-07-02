var request = function(method, url, handler) {
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
};

var xml = function(node) {
    if (node instanceof Array) {
        var result = document.createElement(node[0]);
        for (var i = 1; i < node.length; i++)
            if (typeof node[i] != 'string' && !(node[i] instanceof Array))
                for (var attrName in node[i])
                    result.setAttribute(attrName, node[i][attrName]);
            else
                result.appendChild(xml(node[i]));
        return result;
    }
    else
        return document.createTextNode(node);
};

var empty = function(node) {
    while (node.lastChild) {
        node.removeChild(node.lastChild);
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
            var img = xml(['a', {href: 'https://github.com/' + user.login},
                ['img', {src: user.avatar_url, title: user.login}]]);
            document.querySelector('#github_user_result').appendChild(img);
        });
    });

    document.querySelector('#github_following').addEventListener('click', function(e) {
        e.preventDefault();
        request('GET', e.target.href, function(xhr) {
            JSON.parse(xhr.response)
                .map(function(user) {
                    var img = xml(['a', {href: 'https://github.com/' + user.login},
                        ['img', {src: user.avatar_url, title: user.login, width: 80, height: 80}]]);
                    document.querySelector('#github_following_result').appendChild(img);
                });
        });
    });

    document.querySelector('#github_followers').addEventListener('click', function(e) {
        e.preventDefault();
        request('GET', e.target.href, function(xhr) {
            JSON.parse(xhr.response)
                .map(function(user) {
                    var img = xml(['a', {href: 'https://github.com/' + user.login},
                        ['img', {src: user.avatar_url, title: user.login, width: 80, height: 80}]]);
                    document.querySelector('#github_followers_result').appendChild(img);
                });
        });
    });

    document.querySelector('#facebook_me').addEventListener('click', function(e) {
        e.preventDefault();
        request('GET', e.target.href, function(xhr) {
            JSON.parse(xhr.response)
                .friends.data.map(function(user) {
                    var img = xml(['img', {src: 'https://graph.facebook.com/' + user.id + '/picture', title: user.name }]);
                    document.querySelector('#facebook_me_result').appendChild(img);
                });
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

    document.querySelector("#google_drive_browser").addEventListener("click", function(e) {
        e.preventDefault();
        if (e.target.className == "folder") { 
            var ul = e.target.parentNode.querySelector('ul');
            empty(ul);
            request("GET", e.target.href, function(xhr) {
                JSON.parse(xhr.response)
                    .items.map(function(item) {
                        console.log(item);
                        var li = xml(["li",
                            ["img", {src: item.iconLink}],
                            " ",
                            item.defaultOpenWithLink
                                ? ["a", {href: item.defaultOpenWithLink, "class": "document"}, item.title]
                                : "",
                            item.mimeType == "application/vnd.google-apps.folder"
                                ? ["a", {href: "/oauth/google/request/drive/v2/files?q=\"" + item.id + "\"+in+parents&fields=items(defaultOpenWithLink,iconLink,id,mimeType,thumbnailLink,title)", "class": "folder"},
                                    item.title]
                                : "",
                            item.mimeType == "application/vnd.google-apps.folder"
                                ? ["ul"]
                                : ""
                        ]);
                        ul.appendChild(li);
                    });
            });
        }
        else if (e.target.className == "document") {
            window.open(e.target.href)
        }
    });
});
