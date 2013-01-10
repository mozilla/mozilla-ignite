// This is the list of "link nodes" appearing in the video.
ignite.link_node_manager.content = [
    null, // First element is empty. This will be filled in by another file.
    /* Content is arranged in groups. Each group has a begin and end time.
     * Within each group, each node has a begin time.
     * Nodes with a set position will appear outside the node list.
     */
    {time_in: 12, time_out: 32, content: [
        {resource_id: "about_webrtc", time_in: 13},
        {resource_id: "about_webrtc.webrtc_org", time_in: 15}
    ]},
    {time_in: 47, time_out: 77, content: [
        {resource_id: "background.cloud", time_in: 48},
        {resource_id: "background.tcp", time_in: 56},
        {resource_id: "background.udp", time_in: 57},
        {resource_id: "contributors.kenny_katzgrau", time_in: 68}
    ]},
    {time_in: 119, time_out: 136, content: [
        {resource_id: "background.vulnerabilities", time_in: 120},
        {resource_id: "assorted.flash_thoughts", time_in: 127}
    ]},
    {time_in: 144, time_out: 160, content: [
        {resource_id: "background.ajax", time_in: 147}
    ]},
    {time_in: 204, time_out: 215, content: [
        {resource_id: "assorted.webrtc_io", time_in: 207},
        {resource_id: "assorted.file_api", time_in: 209}
    ]},
    {time_in: 219, time_out: 229, content: [
        {resource_id: "contributors.anants_blog", time_in: 220}
    ]},
    {time_in: 295, time_out: 327, content: [
        {resource_id: "contributors.rob_hawkes", time_in: 296},
        {resource_id: "assorted.point_clouds", time_in: 319}
    ]},
    {time_in: 389, time_out: 422, content: [
        {resource_id: "assorted.twine", time_in: 390},
        {resource_id: "assorted.ninja_blocks", time_in: 399},
        {resource_id: "assorted.raspberry_pi", time_in: 405},
        {resource_id: "assorted.firefox_os", time_in: 411}
    ]},
    {time_in: 444, time_out: 456, content:[
        {resource_id: "assorted.firefox_nightly", time_in: 445},
        {resource_id: "assorted.chrome_canary", time_in: 448}
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
    {id: "about_webrtc", title: 'WebRTC', content: [
        {id: "learn_webrtc", title: 'Learn WebRTC', content: [
            {id: "quickstart", title: "Quickstart", content: "http://www.html5rocks.com/en/tutorials/webrtc/basics/"},
            {id: "getusermedia", title: "getUserMedia()", content: "http://www.html5rocks.com/en/tutorials/getusermedia/intro/"},
            {id: "peer_connection_api", title: "Peer Connection", content: "https://webrtc-demos.appspot.com/html/pc1.html"}
        ]},
        {id: "webrtc_org", title: "WebRTC.org", content: "http://www.webrtc.org"},
        {id: "webrtc_wikipedia", title: 'Wikipedia', content: 'http://en.wikipedia.org/wiki/WebRTC'},
        {id: "w3c_specs", title: "W3C Specs", content: "http://dev.w3.org/2011/webrtc/editor/getusermedia.html"},
        {id: "google_io", title: "Google I/O", content: "http://www.youtube.com/watch?v=E8C8ouiXHHk#t=24m35s"}
    ]},
    {id: "background", title: "Background", content: [
        {id: "ajax",              title: "AJAX",             content: "http://en.wikipedia.org/wiki/Ajax_%28programming%29"},
        {id: "vulnerabilities",   title: "Vulnerabilities",  content: "http://en.wikipedia.org/wiki/Browser_security#Plugins_and_extensions"},
        {id: "cloud",             title: "Cloud Computing",  content: "http://en.wikipedia.org/wiki/Cloud_computing"},
        {id: "tcp",               title: "TCP",              content: "http://en.wikipedia.org/wiki/Transmission_Control_Protocol"},
        {id: "udp",               title: "UDP",              content: "http://en.wikipedia.org/wiki/User_Datagram_Protocol"},
    ]},
    {id: "contributors", title: "Contributors", content:[
        {id: "kenny_katzgrau", title: "Kenny's Blog", content: "http://codefury.net/"},
        {id: "anants_blog", title: "Anant's Blog", content: "http://kix.in/"},
        {id: "rob_hawkes", title: "Rob's Blog", content: "http://rawkes.com/"}
    ]},
    {id: "assorted", display: "none", content: [
        {id: "flash_thoughts",    title: "Flash on Mobile",  content: "http://www.apple.com/hotnews/thoughts-on-flash/"},
        {id: "webrtc_io",         title: "WebRTC.io",        content: "https://github.com/webRTC/webRTC.io"},
        {id: "file_api",          title: "File API",         content: "https://developer.mozilla.org/en-US/docs/Using_files_from_web_applications"},
        {id: "point_clouds",      title: "Point Clouds",     content: "http://en.wikipedia.org/wiki/Point_cloud"},
        {id: "twine",             title: "Twine",            content: "http://supermechanical.com/"},
        {id: "ninja_blocks",      title: "Ninja Blocks",     content: "http://new.ninjablocks.com/"},
        {id: "raspberry_pi",      title: "Raspberry Pi",     content: "http://www.raspberrypi.org/"},
        {id: "firefox_os",        title: "Firefox OS",       content: "http://www.mozilla.org/en-US/firefoxos/"},
        {id: "firefox_nightly",   title: "Firefox Nightly",  content: "https://hacks.mozilla.org/2012/11/progress-update-on-webrtc-for-firefox-on-desktop/"},
        {id: "chrome_canary",     title: "Chrome Canary",    content: "https://www.google.com/intl/en/chrome/browser/canary.html"}
    ]}
];