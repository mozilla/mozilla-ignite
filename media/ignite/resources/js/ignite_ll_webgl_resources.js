// This is the list of "link nodes" appearing in the video.
// TODO: Discuss wether to pause when clicking outside links.
ignite.link_node_manager.content = [
	null, // First element is empty. This will be filled in by another file.
    /* Content is arranged in groups. Each group has a begin and end time.
     * Within each group, each node has a begin time.
     * Nodes with a set position will appear outside the node list.
     */
    {time_in: 54, time_out: 70, content: [
        {title: "WebGL", time_in: 56},
        {title: "Hardware Accel.", time_in: 58},
        {title: "OpenGL", time_in: 64},
        {title: "&lt;Canvas&gt;", time_in: 67},
    ]},
	{time_in: 79, time_out: 90, content: [
        {title: "Working Group", time_in: 80},
        {title: "Khronos Group", time_in: 82}
	]},
	{time_in: 109, time_out: 129, content: [
		{title: "Demos", time_in: 110},
		{title: "Asset Demos", time_in: 115},
		{title: "3DFX Ad", time_in: 119, content: "http://www.youtube.com/watch?v=ooLO2xeyJZA"}
	]},
	{time_in: 154, time_out: 204, content: [
		{title: "Java & OpenGL", time_in: 155, content: "http://www.opengl.org/resources/bindings/"},
        {title: "Dependencies", time_in: 180, content: "http://en.wikipedia.org/wiki/Dependency_hell"},
        {title: "Coupling", time_in: 183, content: "http://en.wikipedia.org/wiki/Coupling_(computer_science)"},
        {title: "Conformance", time_in: 196},
	]},
	{time_in: 206, time_out: 216, content: [
		{title: "TeamUp", time_in: 207, content: "http://www.getteamup.com"}
	]},
	{time_in: 265, time_out: 280, content: [
        {title: "Boot to Gecko", time_in: 265, content: "http://www.mozilla.org/en-US/b2g/"},
        {title: "Firefox OS", time_in: 270, conent: "http://www.digitaltrends.com/mobile/firefox-os-can-mozilla-move-to-mobile-phones/For"}
	]},
	{time_in: 339, time_out: 357, content: [
        {title: "Andor Salga", time_in: 341, content: "http://asalga.wordpress.com/"},
        {title: "XB Pointstream", time_in: 345, content: "http://zenit.senecac.on.ca/wiki/index.php/XB_PointStream"},
        {title: "Point Clouds", time_in: 348}
	]},
	{time_in: 363, time_out: 393, content: [
        {title: "Planet WebGL", time_in: 364, content: "http://planet-webgl.org/"},
		{title: "Giles Thomas", time_in: 367, content: "http://learningwebgl.com/blog/"},
        {title: "Kinect Hacks", time_in: 383, content: "http://www.kinecthacks.com/"}
	]},
	{time_in: 405, time_out: 440, content: [
        {title: "GIS", time_in: 406, content: "http://en.wikipedia.org/wiki/Geographic_information_system"},
        {title: "Visualizations", time_in: 428},
        {title: "Processing.js", time_in: 430, content: "http://processingjs.org/"}
	]},
	{time_in: 467, time_out: 500, content: [
        {title: "3D Conferencing", time_in: 468, content: "https://mozillaignite.org/ideas/323/"},
        {title: "RADIOHEAD WebGL", time_in: 473, content: "http://www.youtube.com/watch?v=oLrsguw1Zac"},
        {title: "(Source)", time_in: 490, content: "http://asalga.wordpress.com/2011/09/02/house-of-cards-webgl-demo-source/"}
	]}
];

// This is the expandable list in the resource section.
ignite.resources.content = [
    {title: 'Mozilla Ignite', content: [
		{title: 'Official', content: [
			{title: 'Official Site', content: 'http://www.mozillaignite.org'},
			{title: 'Twitter', content: 'http://twitter.com/MozillaIgnite'},
			{title: 'NSF.gov', content: 'http://www.nsf.gov/'}
		]},
		{title: 'Press', content: [
			{title: 'White House', content: 'http://www.whitehouse.gov/the-press-office/2012/06/13/we-can-t-wait-president-obama-signs-executive-order-make-broadband-const'},
			{title: 'Launch Day Video', content: 'http://www.youtube.com/watch?v=H-t26owiZUQ'},
			{title: 'Mark Surman', content: 'http://www.nsf.gov/news/news_videos.jsp?cntn_id=124472&media_id=72664&org=NSF'}
		]},
		{title: 'Events', content: [
			{title: 'Hackanooga!', content: 'http://hackanooga-2012.eventbrite.com/'}
		]},
		{title: 'GENI', content: [
			{title: 'Official Site', content: 'http://www.geni.net/'},
			{title: 'Wikipedia', content: 'http://en.wikipedia.org/wiki/Global_Environment_for_Network_Innovations'},
			{title: 'Kenny on GENI, 1', content: 'http://www.screenr.com/2KL8'},
			{title: 'Kenny on GENI, 2', content: 'http://www.screenr.com/FIz8'}
		]}
	]},
    {title: 'About WebGL', content: [
		{title: 'Advantages', content: [
			{title: 'Hardware Accel.', content: 'http://en.wikipedia.org/wiki/Hardware_acceleration'},
			{title: 'Cross Platform', content: 'http://en.wikipedia.org/wiki/Cross-platform'}
		]},
		{title: 'Conformance', content: [
			{title: 'Home', content: 'http://www.khronos.org/webgl/wiki/Testing/Conformance'},
			{title: 'Readme', content: 'https://www.khronos.org/registry/webgl/sdk/tests/README.txt'},
			{title: 'Test', content: 'https://www.khronos.org/registry/webgl/sdk/tests/webgl-conformance-tests.html'}
		]},
		{title: 'Open GL', content: [
			{title: 'Wikipedia', content: 'http://en.wikipedia.org/wiki/OpenGL'},
			{title: 'Resources', content: 'http://www.opengl.org/resources/'},
			{title: 'Open GL ES 2.0', content: 'http://www.khronos.org/opengles/2_X/'}
		]},
		{title: 'Wikipedia', content: 'http://en.wikipedia.org/wiki/Webgl'},
		{title: 'WebGL Portal', content: 'http://www.khronos.org/webgl/'},
		{title: 'GitHub', content: 'https://github.com/KhronosGroup/WebGL'},
		{title: 'Khronos Group', content: 'http://www.khronos.org/'}
	]},
	{title: 'Learn WebGL', content: [
		{title: '&lt;Canvas&gt;', content: [
			{title: 'Wikipedia', content: 'http://en.wikipedia.org/wiki/Canvas_element'},
			{title: 'Canvas Tutorial', content: 'https://developer.mozilla.org/en-US/docs/Canvas_tutorial'}
		]},
		{title: 'Point Clouds', content: [
			{title: 'XB PointStream', content: 'http://zenit.senecac.on.ca/wiki/index.php/XB_PointStream'},
			{title: 'PointClouds.org', content: 'http://pointclouds.org/documentation/'},
			{title: "Andor's Blog", content: 'http://asalga.wordpress.com/portfolio/'}
		]},
		{title: 'GitHub', content: 'https://github.com/KhronosGroup/WebGL'},
		{title: 'Planet WebGL', content: 'http://planet-webgl.org/'},
		{title: 'Giles Thomas', content: 'http://learningwebgl.com/blog/'},
		{title: 'Gregg Tavares', content: 'http://greggman.com/'},
		{title: 'Reference Card', content: 'http://www.khronos.org/files/webgl/webgl-reference-card-1_0.pdf'}
	]},
	{title: 'Demos', content: [
		{title: 'Big Demo Pages', content: [
			{title: 'Mozilla', content: 'https://developer.mozilla.org/en-US/demos/tag/tech:webgl'},
			{title: 'Google Chrome', content: 'http://www.chromeexperiments.com/webgl/'}
		]},
		{title: 'Game Demos', content: []},
		{title: 'Visualizations', content: []},
		{title: 'Featured in Video', content: []},
		{title: 'Featured in Video', content: []} // TODO: Remember to ask Mike about "grey link" attributions.
	]}
];