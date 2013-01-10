// This is the list of "link nodes" appearing in the video.
ignite.link_node_manager.content = [
    null, // First element is empty. This will be filled in by another file.
    /* Content is arranged in groups. Each group has a begin and end time.
     * Within each group, each node has a begin time.
     * Nodes with a set position will appear outside the node list.
     */
    {time_in: 12, time_out: 32, content: [
        {resource_id: "about_webrtc", time_in: 13},
        {resource_id: "about_webrtc.webrtc_org", time_in: 15},
        {resource_id: "assorted.codec_wars", time_in: 25},
    ]},
    {time_in: 33, time_out: 55, content: [
        {resource_id: "demos.sample_app", time_in: 34},
        {resource_id: "about_webrtc.learn_webrtc.quickstart", time_in: 39},
        {resource_id: "about_webrtc.learn_webrtc.getusermedia", time_in: 44},
        {resource_id: "about_webrtc.learn_webrtc.peer_connection_api", time_in: 47},
    ]},
    {time_in: 65, time_out: 104, content: [
        {resource_id: "contributors.anants_blog", time_in: 66},
        {resource_id: "assorted.ietf", time_in: 69},
        {resource_id: "about_webrtc.w3c_specs", time_in: 73},
        {resource_id: "demos.data_channel_test", time_in: 96}
    ]},
    {time_in: 113, time_out: 154, content: [
        {resource_id: "contributors.tokbox.website", time_in: 114},
        {resource_id: "contributors.tokbox.opentok_library", time_in: 119},
        {resource_id: "contributors.ian_on_webrtc", time_in: 133},
        {resource_id: "articles.techcrunch", time_in: 146}
    ]},
    {time_in: 195, time_out: 222, content: [
        {resource_id: "demos.head_tracking", time_in: 196},
        {resource_id: "assorted.web_access", time_in: 200},
        {resource_id: "assorted.cebp", time_in: 215}
    ]},
    {time_in: 246, time_out: 287, content: [
        {resource_id: "contributors.big_blue_button", time_in: 247},
        {resource_id: "contributors.big_blue_button.submission", time_in: 270},
        {resource_id: "articles.ericson", time_in: 278},
        {resource_id: "articles.gov_adopt", time_in: 280}
    ]},
    {time_in: 341, time_out: 391, content: [
        {resource_id: "assorted.sdn", time_in: 342},
        {resource_id: "articles.openflow", time_in: 346},
        {resource_id: "assorted.voip", time_in: 349},
        {resource_id: "assorted.telemedicine", time_in: 379},
        {}
    ]},
    {time_in: 400, time_out: 419, content: [
        {resource_id: "contributors.justin.google", time_in: 401},
        {resource_id: "contributors.justin.wayback", time_in: 408},
        {resource_id: "assorted.google_video_chat", time_in: 410},
        {resource_id: "assorted.google_hangouts", time_in: 412}
    ]},
    {time_in: 423, time_out: 455, content: [
        {resource_id: "assorted.bit_rates", time_in: 424},
        {resource_id: "assorted.compression", time_in: 427},
        {resource_id: "assorted.data_rate_units", time_in: 448}
    ]},
    {time_in: 529, time_out: 541, content:[
        {resource_id: "assorted.chrome_canary", time_in: 530},
        {resource_id: "assorted.firefox_nightly", time_in: 532}
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
        {id: "webrtc_wikipedia", title: 'Wikipedia', content: 'http://en.wikipedia.org/wiki/Webrtc'},
        {id: "w3c_specs", title: "W3C Specs", content: "http://dev.w3.org/2011/webrtc/editor/getusermedia.html"}
    ]},
    {id: "demos", title: 'Demos', content: [
        {id: "head_tracking", title: "Head-Tracking", content: "http://auduno.tumblr.com/post/25125149521/head-tracking-with-webrtc"},
        {id: "sample_app", title: "Sample App", content: "https://code.google.com/p/libjingle/source/browse/#svn%2Ftrunk%2Ftalk%2Fexamples%2Fpeerconnection%2Fclient"},
        {id: "data_channel_test", title: "Data Test", content: "http://people.mozilla.com/~anarayanan/webrtc/data_test.html"}
    ]},
    {id: "articles", title: "Articles & Posts", content: [
        {id: "techcrunch",        title: "TechCrunch",       content: "http://techcrunch.com/2012/11/05/tokboxs-opentok-webrtc/"},
        {id: "openflow",          title: "OpenFlow",         content: "http://en.wikipedia.org/wiki/OpenFlow"},
        {id: "gov_adopt",         title: "Gov. Adoption",    content: "http://www.fedtechmagazine.com/article/2012/09/8-reasons-why-government-adopting-video-conferencing-infographic"},
        {id: "ericson",           title: "Ericson Review",   content: "http://www.ericsson.com/news/120405_webrtc_enhancing_the_web_with_real-time_communication_capabilities_244159019_c?categoryFilter=ericsson_review_1270673222_c"},
    ]},
    {id: "contributors", title: "Contributors", content:[
        {id: "justin", title: "Justin Uberti", content: [
            {id: "wayback",    title: "Justin Wayback",   content: "http://web.archive.org/web/20070518195017/http://journals.aol.com/juberti/runningman/"},
            {id: "google",     title: "Justin@Google",    content: "http://www.youtube.com/watch?v=E8C8ouiXHHk"},
        ]},
        {id: "tokbox", title: "TokBox", content: [
            {id: "website", title: "Website", content: "http://tokbox.com/"},
            {id: "opentok_lib", title: "OpenTok Library", content: "http://tokbox.com/opentok/api/documentation/gettingstarted"}
        ]},
        {id: "big_blue_button", title: "BigBlueButton", content: [
            {id: "website", title: "Website", content: "http://www.bigbluebutton.org/"},
            {id: "blog", title: "Blog", content: "http://www.bigbluebutton.org/blog/"},
            {id: "submission", title: "Ignite Submission", content: "https://mozillaignite.org/ideas/215/"}
        ]},
        {id: "ian_on_webrtc", title: "Ian on WebRTC", content: "http://www.tokbox.com/blog/opentok-on-webrtc-grab-your-lab-coat/"},
        {id: "anants_blog", title: "Anant's Blog", content: "http://kix.in/"}
    ]},
    {id: "assorted", display: "none", content: [
        {id: "google_video_chat", title: "Google Vid. Chat", content: "https://www.google.com/chat/video"},
        {id: "google_hangouts",   title: "Google Hangouts",  content: "http://www.google.com/+/learnmore/hangouts/"},
        
        {id: "chrome_canary",     title: "Chrome Canary",    content: "https://tools.google.com/dlpage/chromesxs"},
        {id: "firefox_nightly",   title: "Firefox Nightly",  content: "http://nightly.mozilla.org/"},
        
        {id: "sdn",               title: "SDN",              content: "http://en.wikipedia.org/wiki/Software-defined_networking"},
        {id: "cebp",              title: "CEBP",             content: "http://en.wikipedia.org/wiki/Communication-enabled_business_process"},
        {id: "bit_rates",         title: "Bit Rates List",   content: "http://en.wikipedia.org/wiki/List_of_device_bit_rates"},
        {id: "compression",       title: "Compression",      content: "http://en.wikipedia.org/wiki/Video_compression#Video"},
        {id: "data_rate_units",   title: "Data rate units",  content: "http://en.wikipedia.org/wiki/Data_rate_units"},
        {id: "voip",              title: "VOIP",             content: "http://en.wikipedia.org/wiki/Voice_over_IP"},
        {id: "telemedicine",      title: "Telemedicine",     content: "http://en.wikipedia.org/wiki/Telemedicine"},
        {id: "ietf",              title: "IETF",             content: "http://www.ietf.org/"},
        {id: "web_access",        title: "Accessibiliity",   content: "http://www.w3.org/WAI/"},
        {id: "codec_wars",        title: "Codec Wars",       content: "http://news.softpedia.com/news/Mozilla-May-Have-Won-the-Codec-Wars-for-WebRTC-Before-They-Even-Started-288822.shtml"},
    ]}
];