NodeList.prototype.toArray = function() { return Array.prototype.slice.call(this); };

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
            if (typeof node[i] == 'object' && !(node[i] instanceof Array))
                for (var attrName in node[i])
                    result.setAttribute(attrName, node[i][attrName]);
            else
                result.appendChild(xml(node[i]));
        return result;
    }
    else
        return document.createTextNode(node.toString());
};

var empty = function(node) {
    while (node.lastChild) {
        node.removeChild(node.lastChild);
    }
}

document.addEventListener('DOMContentLoaded', function(e) {
    request('GET', '/oauth/session/check/', function(xhr) {
        document.querySelector('#session_id').textContent = document.cookie;

        document.querySelectorAll("a.authorize")
            .toArray()
            .forEach(function(link) {
                link.href += link.href.indexOf("?") > -1
                    ? "&" + document.cookie
                    : "?" + document.cookie;
                link.focus();
                link.blur();
        });
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

    document.querySelector('#github_repos').addEventListener('click', function(e) {
        e.preventDefault();
        request('GET', e.target.href, function(xhr) {
            console.log(JSON.parse(xhr.response));
            JSON.parse(xhr.response)
                .map(function(repo) {
                    var p = xml(['div', 
                        ['a', {href:repo.html_url}, repo.name],
                        ': ', repo.watchers, ' stars, ',
                        ' ', repo.forks, ' forks',
                        ' ', repo.open_issues, ' issues']);
                    document.querySelector('#github_repos_result').appendChild(p);
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

    document.querySelector("#live_skydrive_browser").addEventListener("click", function(e) {
        var isFolder = function(item) { return item.type == "folder" || item.type == "album"; }
        var isDocument = function(item) { return item.type == "file" || item.type == "photo"; }
        e.preventDefault();
        if (e.target.className == "folder") {
            request("GET", e.target.href, function(xhr) {
                var ul = e.target.parentNode.querySelector('ul');
                empty(ul);
                JSON.parse(xhr.response)
                    .data.map(function(item) {
                        console.log(item);
                        var li = xml(["li",
                            isFolder(item)
                                ? ["a", {href: "/oauth/live/api/" + item.id + "/files", "class": "folder"}, item.name]
                                : "",
                            isDocument(item)
                                ? ["a", {href: item.link, "class": "document"}, item.name]
                                : "",
                            isFolder(item)
                                ? ["ul"]
                                : ""
                        ]);
                        ul.appendChild(li);
                    });
            });
        }
        else if (e.target.className = "document") {
            window.open(e.target.href)
        }
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
                            item.mimeType != "application/vnd.google-apps.folder"
                                ? ["a", {href: item.alternateLink, "class": "document"}, item.title]
                                : "",
                            item.mimeType == "application/vnd.google-apps.folder"
                                ? ["a", {href: "/oauth/google/api/drive/v2/files?q=\"" + item.id + "\"+in+parents&fields=items(alternateLink,defaultOpenWithLink,iconLink,id,mimeType,thumbnailLink,title)", "class": "folder"},
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

    document.querySelector("#dropbox_me").addEventListener("click", function(e) {
        e.preventDefault();
        request("GET", e.target.href, function(xhr) {
            var me = JSON.parse(xhr.response);
            document.querySelector("#dropbox_me_result").textContent = me.display_name 
                + " <"
                + me.email
                + ">";
        });
    });

    document.querySelector("#dropbox_browser").addEventListener("click", function(e) {
        e.preventDefault();
        if (e.target.className == "folder") {
            var ul = e.target.parentNode.querySelector("ul");
            empty(ul);
            request("GET", e.target.href, function(xhr) {
                JSON.parse(xhr.response)
                    .contents.map(function(item) {
                        console.log(item);
                        var path = item.path.split("/").map(encodeURIComponent).join("/");
                        var name = item.path.split("/").pop();
                        var li = xml([
                            "li",
                            ["img", {src: "/oauth/dropbox/" + item.icon + ".gif"}],
                            " ",
                            item.is_dir 
                                ? ["a", {href: "/oauth/dropbox/api/1/metadata/dropbox" + path, "class": "folder"}, name]
                                : ["a", {href: "/oauth/dropbox/api/1/media/dropbox" + path, "class": "document"}, name],
                            item.is_dir ? ["ul"] : ""
                        ]);
                        ul.appendChild(li);
                    });
            });
        }
        else if (e.target.className == "document") {
            request("GET", e.target.href, function(xhr) {
                var media = JSON.parse(xhr.response);
                window.open(media.url);
            });
        }
    });
    
    document.querySelector("#linkedin_me").addEventListener("click", function(e) {
        e.preventDefault();
        request("GET", e.target.href, function(xhr) { 
            document.querySelector("#linkedin_me_result").textContent 
                = xhr.responseXML.querySelector("person first-name").textContent
                + " "
                + xhr.responseXML.querySelector("person last-name").textContent
                + ", "
                + xhr.responseXML.querySelector("person headline").textContent;
        });
    });
    
    document.querySelector("#linkedin_friends").addEventListener("click", function(e) {
        e.preventDefault();
        request("GET", e.target.href, function(xhr) {
            var div = document.querySelector("#linkedin_friends_result");
            xhr.responseXML
                .querySelectorAll("connections person")
                .toArray()
                .forEach(function(person) {
                    if (person.querySelector("id").textContent == "private")
                        return;
                    var picture = person.querySelector("picture-url");
                    if (!picture)
                        return;
                    var img = xml(["img", {
                        src: picture.textContent,
                        title: person.querySelector("first-name").textContent
                            + " "
                            + person.querySelector("last-name").textContent
                    }]);
                    div.appendChild(img);
                });
       });
    });

    document.querySelector("#reddit_me").addEventListener("click", function(e) {
        e.preventDefault();
        request("GET", e.target.href, function(xhr) {
            var me = JSON.parse(xhr.response);
            document.querySelector("#reddit_me_result").textContent
                = me.name
                + " ("
                + me.link_karma
                + " link karma, "
                + me.comment_karma
                + " comment karma)";
        });
    });

    document.querySelector("#linkbag").addEventListener("click", function(e) {
        e.preventDefault();
        if (e.target.href) { 
            window.open(e.target.href);
        }
    });
});
