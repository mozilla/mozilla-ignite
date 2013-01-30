// This is the list of "link nodes" appearing in the video.
ignite.link_node_manager.content = [
    null, // First element is empty. This will be filled in by another file.
    /* Content is arranged in groups. Each group has a begin and end time.
     * Within each group, each node has a begin time.
     * Nodes with a set position will appear outside the node list.
     */
    {time_in: 11, time_out: 31, content: [
        {resource_id: "websockets", time_in: 12},
        {resource_id: "assorted.duplex", time_in: 17},
        {resource_id: "contributors.rob_hawkes", time_in: 23}
    ]},
    {time_in: 48, time_out: 55, content: [
        {resource_id: "assorted.ajax", time_in: 49}
    ]},
    {time_in: 55, time_out: 66, content: [
        {resource_id: "contributors.peter_lubbers", time_in: 56},
        {resource_id: "assorted.kaazing", time_in: 58}
    ]},
    {time_in: 68, time_out: 76, content:[
        {resource_id: "websockets.websocket_org.about", time_in: 68}
    ]},
    {time_in: 168, time_out: 177, content: [
        {resource_id: "websockets.dzone_article", time_in: 168}
    ]},
    {time_in: 191, time_out: 202, content: [
        {resource_id: "assorted.nodejs", time_in: 192},
        {resource_id: "websockets.tutorials.socketio", time_in: 194}
    ]},
    {time_in: 214, time_out: 267, content: [
        {resource_id: "contributors.tom_croucher", time_in: 215},
        {resource_id: "assorted.cloud9ide", time_in: 237},
        {resource_id: "assorted.change", time_in: 251},
        {resource_id: "assorted.etherpad", time_in: 261}
    ]},
    {time_in: 268, time_out: 279, content: [
        {resource_id: "contributors.ondrej_zara", time_in: 269},
        {resource_id: "assorted.dev_derby", time_in: 272}
    ]},
    {time_in: 324, time_out: 332, content: [
        {resource_id: "contributors.rob_hawkes.rawkets", time_in: 325}
    ]},
    {time_in: 424, time_out: 466, content: [
        {resource_id: "assorted.kaazing_financial", time_in: 427},
        {resource_id: "websockets.games.buildnewgames", time_in: 431},
        {resource_id: "assorted.kaazing_betting", time_in: 445},
        {resource_id: "assorted.sentiment_tracking", time_in: 455},
        {resource_id: "assorted.inventory_tracking", time_in: 458}
    ]},
    {time_in: 493, time_out: 508, content: [
        {resource_id: "assorted.pointclouds", time_in: 494},
        {resource_id: "assorted.teamup", time_in: 500}
    ]}
];
// This is the expandable list in the resource section.
ignite.resources.content = [
    {id: "mozilla_ignite", title: 'Mozilla Ignite', content: [
        {id: "official", title: 'Official', content: [
            {id: "official_site", title: 'Official Site', content: 'http://www.mozillaignite.org'},
            {id: "twitter", title: 'Twitter', content: 'http://twitter.com/MozillaIgnite'},
            {id: "us_ignite", title: 'US Ignite', content: 'http://us-ignite.org/'},
            {id: "nsf_gov", title: 'NSF.gov', content: 'http://www.nsf.gov/'}
        ]},
        {id: "press", title: 'Press', content: [
            {id: "white_house", title: 'White House', content: 'http://www.whitehouse.gov/the-press-office/2012/06/13/we-can-t-wait-president-obama-signs-executive-order-make-broadband-const'},
            {id: "launch_day_video", title: 'Launch Day Video', content: 'http://www.youtube.com/watch?v=H-t26owiZUQ'},
            {id: "mark_surman", title: 'Mark Surman', content: 'http://www.nsf.gov/news/news_videos.jsp?cntn_id=124472&media_id=72664&org=NSF'}
        ]},
        {id: "geni", title: 'GENI', content: [
            {id: "geni_site", title: 'Official Site', content: 'http://www.geni.net/'},
            {id: "geni_wikipedia", title: 'Wikipedia', content: 'http://en.wikipedia.org/wiki/Global_Environment_for_Network_Innovations'},
            {id: "kenny_1", title: 'Kenny on GENI, 1', content: 'http://www.screenr.com/2KL8'},
            {id: "kenny_2", title: 'Kenny on GENI, 2', content: 'http://www.screenr.com/FIz8'}
        ]}
    ]},
    {id: "websockets", title: 'Websockets', content: [
        {id: "tutorials", title: "Learn Websocket", content: [
            {id: "mdn_websockets", title: "MDN Websockets", content: "https://developer.mozilla.org/en-US/docs/WebSockets"},
            {id: "socketio", title: "Socket IO", content: "http://socket.io/"}
        ]},
        {id: "websocket_org", title: "Websocket.org", content: [
            {id: "website", title: "Main Page", content: "http://www.websocket.org/"},
            {id: "demos", title: "Demos", content: "http://www.websocket.org/demos.html"},
            {id: "about", title: "About Websocket", content: "http://www.websocket.org/aboutwebsocket.html"}
        ]},
        {id: "dzone_article", title: "DZone Article", content: "http://refcardz.dzone.com/refcardz/html5-websocket"},
        {id: "games", title: "Games", content: [
            {id: "game_on", title: "Game On", content: "https://gameon.mozilla.org/en-US/"},
            {id: "buildnewgames", title: "Build New Games", content: "http://buildnewgames.com/websockets/"}
        ]}
    ]},
    {id: "contributors", title: "Contributors", content:[
        {id: "rob_hawkes", title: "Rob Hawkes", content: [
            {id: "website", title: "Rob's Blog", content: "http://rawkes.com/"},
            {id: "rawkets", title: "Rawkets", content: "http://rawkets.com/"},
            {id: "twitter", title: "Twitter", content: "https://twitter.com/robhawkes"},
            {id: "github", title: "Github", content: "https://github.com/robhawkes"},
            {id: "interview", title: "Marakana TechTV", content: "http://www.youtube.com/watch?v=KxylQ3W2iqE"}
        ]},
        {id: "peter_lubbers", title: "Peter Lubbers", content: [
            {id: "website", title: "Peter's Twitter", content: "https://twitter.com/peterlubbers"},
            {id: "interview", title: "Marakana TechTV", content: "http://www.youtube.com/watch?v=g2qYAd1vUdc"},
            {id: "articles", title: "Articles", content: "http://peterlubbers.sys-con.com/"},
            {id: "user_group", title: "SFHTML5.org", content: "http://www.sfhtml5.org/"},
            {id: "pro_html5", title: "ProHTML5.org", content: "http://www.prohtml5.com/"}
        ]},
        {id: "tom_croucher", title: "Tom H-C", content: [
            {id: "website", title: "Website", content: "http://tomhughescroucher.com/"},
            {id: "twitter", title: "Twitter", content: "https://twitter.com/sh1mmer"},
            {id: "github", title: "Github", content: "https://github.com/sh1mmer"}
        ]},
        {id: "ondrej_zara", title: "Ondrej &#381;&#225;ra", content: [ // League Gothic does not display a useable character at &#345;
            {id: "website", title: "Website", content: "http://ondras.zarovi.cz/"},
            {id: "twitter", title: "Twitter", content: "https://twitter.com/0ndras/"},
            {id: "github", title: "Github", content: "https://github.com/ondras/"},
            {id: "interview", title: "Interview", content: "https://hacks.mozilla.org/2012/08/interview-ondrej-zara-websockets-dev-derby-winner/"}
        ]}
    ]},
    {id: "assorted", display: "none", content: [
        {id: "duplex", title: "Full Duplex", content: "http://en.wikipedia.org/wiki/Duplex_%28telecommunications%29"},
        {id: "ajax", title: "AJAX", content: "https://developer.mozilla.org/en-US/docs/AJAX"},
        {id: "teamup", title: "TeamUp", content: "http://www.getteamup.com"},
        {id: "kaazing", title: "Kaazing", content: "http://kaazing.com/"},
        {id: "kaazing_financial", title: "Financial", content: "http://kaazing.com/solutions/financials"},
        {id: "kaazing_betting", title: "Betting", content: "http://kaazing.com/content/customer-case-studies"},
        {id: "sentiment_tracking", title: "Sentiment Tracking", content: "http://en.wikipedia.org/wiki/Sentiment_analysis"},
        {id: "inventory_tracking", title: "Inventory Tracking", content: "http://en.wikipedia.org/wiki/Radio-frequency_identification"},
        {id: "change", title: "Change.org", content: "http://www.change.org"},
        {id: "etherpad", title: "Etherpad", content: "http://etherpad.org/"},
        {id: "cloud9ide", title: "Cloud9 IDE", content: "https://c9.io/"},
        {id: "pointclouds", title: "Point Clouds", content: "http://en.wikipedia.org/wiki/Point_cloud"},
        {id: "nodejs", title: "Node.js", content: "http://nodejs.org"},
        {id: "dev_derby", title: "Dev Derby", content: "https://developer.mozilla.org/en-US/demos/devderby/2012/may"}
    ]}
];