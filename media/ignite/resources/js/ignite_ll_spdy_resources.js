// This is the list of "link nodes" appearing in the video.
ignite.link_node_manager.content = [
    null, // First element is empty. This will be filled in by another file.
    /* Content is arranged in groups. Each group has a begin and end time.
     * Within each group, each node has a begin time.
     * Nodes with a set position will appear outside the node list.
     */
    {time_in: 12, time_out: 23, content: [
        {resource_id: 'about_spdy', time_in: 13}
    ]},
    {time_in: 29, time_out: 85, content: [
        {resource_id: 'contributors.tom_croucher', time_in: 30},
        {resource_id: 'about_spdy.http', time_in: 36},
        {resource_id: 'about_spdy.http.keep_alive', time_in: 52},
        {resource_id: 'about_spdy.http.pipelining', time_in: 77}
    ]},
    {time_in: 102, time_out: 130, content: [
        {resource_id: 'about_spdy.chromium_projects', time_in: 103},
        {resource_id: 'about_spdy.http.http2', time_in: 123},
        {resource_id: 'about_spdy.spdy_and_http2', time_in: 125}
    ]},
    {time_in: 131, time_out: 150, content: [
        {resource_id: 'contributors.josh_aas', time_in: 132},
        {resource_id: 'assorted.tls', time_in: 143}
    ]},
    {time_in: 209, time_out: 219, content: [
        {resource_id: 'assorted.hol_blocking', time_in: 210}
    ]},
    {time_in: 312, time_out: 338, content: [
        {resource_id: 'assorted.latency', time_in: 312},
        {resource_id: 'assorted.latency_rant', time_in: 313},
        {resource_id: 'assorted.round_trip', time_in: 316},
        {resource_id: 'assorted.velocity_factor', time_in: 330}
    ]},
    {time_in: 354, time_out: 408, content: [
        {resource_id: 'assorted.slow_start_wiki', time_in: 355},
        {resource_id: 'assorted.slow_start_article', time_in: 356},
        {resource_id: 'assorted.packet_forwarding', time_in: 400}
    ]},
    {time_in: 419, time_out: 468, content: [
        {resource_id: 'contributors.joel_cox', time_in: 420},
        {resource_id: 'assorted.node_js', time_in: 445},
        {resource_id: 'assorted.express', time_in: 447},
        {resource_id: 'assorted.hogan_js', time_in: 455},
        {resource_id: 'assorted.mustache_js', time_in: 460}
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
    {id: 'about_spdy', title: 'SPDY', content: [
        {id: 'http', title: 'HTTP', content: [
            {id: 'wikipedia', title: 'Wikipedia', content: 'http://en.wikipedia.org/wiki/Http'},
            {id: 'mdn', title: 'Mozilla', content: 'https://developer.mozilla.org/en-US/docs/HTTP'},
            {id: 'keep_alive', title: 'Keep Alive', content: 'http://en.wikipedia.org/wiki/HTTP_persistent_connection'},
            {id: 'pipelining', title: 'Pipelining', content: 'http://en.wikipedia.org/wiki/HTTP_pipelining'},
            {id: 'http2', title: 'HTTP2.0', content: 'http://en.wikipedia.org/wiki/HTTP_2.0'}
        ]},
        {id: 'chromium_projects', title: 'White Paper', content: 'http://www.chromium.org/spdy/spdy-whitepaper'},
        {id: "spdy_wikipedia", title: 'Wikipedia', content: 'http://en.wikipedia.org/wiki/SPDY'},
        {id: 'spdy_and_http2', title: 'SPDY & HTTP2.0', content: 'http://www.infoq.com/news/2012/11/http20-first-draft'},
        {id: 'moz_hacks', title: 'Mozilla Hacks', content: 'http://hacks.mozilla.org/2012/02/spdy-brings-responsive-and-scalable-transport-to-firefox-11/'}
    ]},
    {id: "contributors", title: "Contributors", content:[
        {id: "tom_croucher", title: "Tom H-C", content: [
            {id: "website", title: "Website", content: "http://tomhughescroucher.com/"},
            {id: "twitter", title: "Twitter", content: "https://twitter.com/sh1mmer"},
            {id: "github", title: "Github", content: "https://github.com/sh1mmer"}
        ]},
        {id: "josh_aas", title: "Josh Aas", content: [
            {id: "website", title: "Website", content: "http://joshaas.net/"},
            {id: "blog", title: "Blog", content: "http://boomswaggerboom.wordpress.com"}
        ]},
        {id: "joel_cox", title: "Jo&euml;l Cox", content: [
            {id: "website", title: "Website", content: "http://joelcox.nl/"},
            {id: 'github', title: 'Github', content: 'https://github.com/joelcox'},
            {id: "twitter", title: "Twitter", content: "https://twitter.com/joelcox"}
        ]}
    ]},
    {id: "assorted", display: "none", content: [
        {id: 'tls', title: 'TLS', content: 'http://en.wikipedia.org/wiki/Transport_Layer_Security'},
        {id: 'hol_blocking', title: 'HoL Blocking', content: 'http://en.wikipedia.org/wiki/Head-of-line_blocking'},
        {id: 'latency', title: 'Latency101', content: 'http://www.webperformancetoday.com/2012/04/02/latency-101-what-is-latency-and-why-is-it-such-a-big-deal/'},
        {id: 'latency_rant', title: 'Article on Latency', content: 'http://www.stuartcheshire.org/rants/Latency.html'},
        {id: 'round_trip', title: 'Round-trip Time', content: 'http://www.igvita.com/2012/07/19/latency-the-new-web-performance-bottleneck/'},
        {id: 'velocity_factor', title: 'Velocity Factor', content: 'http://en.wikipedia.org/wiki/Velocity_factor'},
        {id: 'slow_start_wiki', title: 'Slow Start Wiki', content: 'http://en.wikipedia.org/wiki/Slow-start'},
        {id: 'slow_start_article', title: 'Slow Start Article', content: 'http://www.igvita.com/2011/10/20/faster-web-vs-tcp-slow-start/'},
        {id: 'tcp', title: 'TCP', content: ''},
        {id: 'node_js', title: 'Node.js', content: 'http://nodejs.org/'},
        {id: 'express', title: 'Express', content: 'http://expressjs.com/'},
        {id: 'hogan_js', title: 'Hogan.js', content: 'http://twitter.github.com/hogan.js/'},
        {id: 'mustache_js', title: 'Mustache.js', content: 'https://github.com/janl/mustache.js/'},
        {id: 'packet_forwarding', title: 'Packet Forwarding', content: 'http://www.cisco.com/web/about/security/intelligence/network_performance_metrics.html'}
    ]}
];