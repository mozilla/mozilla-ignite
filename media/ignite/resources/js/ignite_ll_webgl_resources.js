// This is the list of "link nodes" appearing in the video.
ignite.link_node_manager.content = [
	null, // First element is empty. This will be filled in by another file.
    /* Content is arranged in groups. Each group has a begin and end time.
     * Within each group, each node has a begin time.
     * Nodes with a set position will appear outside the node list.
     */
    {time_in: 54, time_out: 70, content: [
        {resource_id: "about_webgl", time_in: 56},
        {resource_id: "about_webgl.advantages.hardware_acceleration", time_in: 58},
        {resource_id: "about_webgl.open_gl", time_in: 64},
        {resource_id: "learn_webgl.canvas", time_in: 67},
    ]},
	{time_in: 79, time_out: 90, content: [
        {resource_id: "about_webgl.khronos_group", time_in: 82}
	]},
	{time_in: 109, time_out: 129, content: [
		{resource_id: "demos", time_in: 110},
		{resource_id: "demos.game_demos", time_in: 115},
		{resource_id: "demos.game_demos.3dfx_ad", time_in: 119}
	]},
	{time_in: 154, time_out: 204, content: [
		{resource_id: "assorted.java_&_opengl", time_in: 155},
        {resource_id: "assorted.dependencies", time_in: 180},
        {resource_id: "assorted.coupling", time_in: 183},
        {resource_id: "about_webgl.conformance", time_in: 196}
	]},
	{time_in: 206, time_out: 216, content: [
		{resource_id: "assorted.teamup", time_in: 207}
	]},
	{time_in: 265, time_out: 280, content: [
        {resource_id: "assorted.boot_to_gecko", time_in: 265},
        {resource_id: "assorted.firefox_os", time_in: 270},
        {resource_id: "assorted.glass_skull", time_in: 273}
	]},
    {time_in: 298, time_out: 314, content: [
        {resource_id: "assorted.focus_areas", time_in: 298},
        {resource_id: "learn_webgl.point_clouds", time_in: 304},
        {resource_id: "learn_webgl.point_clouds.andor_salga", time_in: 309},
        {resource_id: "learn_webgl.point_clouds.xb_pointstream", time_in: 310}
    ]},
	{time_in: 315, time_out: 387, content: [
        {resource_id: "learn_webgl.planet_webgl", time_in: 315},
		{resource_id: "learn_webgl.giles_thomas", time_in: 317},
        {resource_id: "assorted.kinect_hacks", time_in: 335},
        {resource_id: "assorted.gis", time_in: 356},
        {resource_id: "assorted.processing_js", time_in: 382}
	]},
    {time_in: 414, time_out: 447, content: [
        {resource_id: "assorted.3d_graphics_math", time_in: 414},
        {resource_id: "assorted.big_blue_button", time_in: 424},
        {resource_id: "assorted.p2pu", time_in: 432},
        {resource_id: "assorted.khan_academy", time_in: 442}
	]},
	{time_in: 460, time_out: 515, content: [
        {resource_id: "assorted.the_gig", time_in: 460},
        {resource_id: "assorted.webgl_exercise", time_in: 493},
        {resource_id: "assorted.andors_submission", time_in: 490},
        {resource_id: "assorted.radiohead_webgl", time_in: 504},
        {resource_id: "assorted.radiohead_source", time_in: 510}
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
    {id: "about_webgl", title: 'About WebGL', content: [
		{id: "advantages", title: 'Advantages', content: [
			{id: "hardware_acceleration", title: 'Hardware Accel.', content: 'http://en.wikipedia.org/wiki/Hardware_acceleration'},
			{id: "cross_platform", title: 'Cross Platform', content: 'http://en.wikipedia.org/wiki/Cross-platform'}
		]},
		{id: "conformance", title: 'Conformance', content: [
			{id: "conformance_home", title: 'Home', content: 'http://www.khronos.org/webgl/wiki/Testing/Conformance'},
			{id: "conformance_readme", title: 'Readme', content: 'https://www.khronos.org/registry/webgl/sdk/tests/README.txt'},
			{id: "conformance_test", title: 'Test', content: 'https://www.khronos.org/registry/webgl/sdk/tests/webgl-conformance-tests.html'}
		]},
		{id: "open_gl", title: 'Open GL', content: [
			{title: 'Wikipedia', content: 'http://en.wikipedia.org/wiki/OpenGL'},
			{title: 'Resources', content: 'http://www.opengl.org/resources/'},
			{title: 'Open GL ES 2.0', content: 'http://www.khronos.org/opengles/2_X/'}
		]},
		{title: 'Wikipedia', content: 'http://en.wikipedia.org/wiki/Webgl'},
		{title: 'WebGL Portal', content: 'http://www.khronos.org/webgl/'},
		{title: 'GitHub', content: 'https://github.com/KhronosGroup/WebGL'},
		{id: "khronos_group", title: 'Khronos Group', content: 'http://www.khronos.org/'}
	]},
	{id: "learn_webgl", title: 'Learn WebGL', content: [
		{id: "canvas", title: '&lt;Canvas&gt;', content: [
			{title: 'Wikipedia', content: 'http://en.wikipedia.org/wiki/Canvas_element'},
			{title: 'Canvas Tutorial', content: 'https://developer.mozilla.org/en-US/docs/Canvas_tutorial'}
		]},
		{id: "point_clouds", title: 'Point Clouds', content: [
			{id: "xb_pointstream", title: 'XB PointStream', content: 'http://zenit.senecac.on.ca/wiki/index.php/XB_PointStream'},
			{title: 'PointClouds.org', content: 'http://pointclouds.org/documentation/'},
			{id: "andor_salga", title: "Andor's Blog", content: 'http://asalga.wordpress.com/portfolio/'}
		]},
		{title: 'GitHub', content: 'https://github.com/KhronosGroup/WebGL'},
		{id: "planet_webgl", title: 'Planet WebGL', content: 'http://planet-webgl.org/'},
		{id: "giles_thomas", title: 'Giles Thomas', content: 'http://learningwebgl.com/blog/'},
		{title: 'MDN Resources', content: 'https://developer.mozilla.org/en-US/docs/WebGL'},
		{title: 'Reference Card', content: 'http://www.khronos.org/files/webgl/webgl-reference-card-1_0.pdf'}
	]},
	{id: "demos", title: 'Demos', content: [
		{title: 'Big Demo Pages', content: [
			{title: 'Mozilla', content: 'https://developer.mozilla.org/en-US/demos/tag/tech:webgl'},
			{title: 'Google Chrome', content: 'http://www.chromeexperiments.com/webgl/'},
			{title: 'ro.me Tech', content: 'http://www.ro.me/tech/'}
		]},
		{id: "game_demos", title: 'Game Demos', content: [
            {title: 'Quake III', content: 'http://media.tojicode.com/q3bsp/'},
            {title: 'League of Legends', content: 'http://www.3dsitelinks.com/3d-art-&-experimental/league-of-legends-viewer/'},
            {title: 'Half-Life Zombie', content: 'http://www.webgl.com/2012/04/webgl-demo-half-life-zombie-model/'},
            {id: "3dfx_ad", title: "3DFX Ad", content: "http://www.youtube.com/watch?v=ooLO2xeyJZA"}
        ]},
		{title: 'Video Features 1', content: [
            {title: 'One Millionth Tower', content: 'http://highrise.nfb.ca/onemillionthtower/'},
            {title: 'Turbulent Point Cloud', content: 'http://www.ro.me/tech/turbulent-point-cloud'},
            {title: 'Hatching Glow Shader', content: 'http://www.ro.me/tech/hatching-glow-shader'},
            {title: 'Kai &apos;Opua', content: 'http://www.webgl.com/2012/05/webgl-game-kai-opua/'},
            {title: 'ro.me', content: 'http://www.ro.me/'},
            {title: 'Shiny Knot', content: 'http://www.chromeexperiments.com/detail/floating-shiny-knot/'},
            {title: 'Slice Drop', content: 'https://developer.mozilla.org/en-US/demos/detail/slicedrop'},
            {title: '3D Grapher', content: 'http://www.chromeexperiments.com/detail/3d-grapher/?f=webgl'}
        ]},
		{title: 'Video Features 2', content: [
            {title: 'Solar System', content: 'https://developer.mozilla.org/en-US/demos/detail/solar-system'},
            {title: 'Glass Skull', content: 'http://www.webgl.com/2012/02/webgl-demo-glass-skull/'},
            {title: 'Andor&apos;s Demos', content: 'http://scotland.proximity.on.ca/asalga/'},
            {title: 'Island of Maui', content: 'http://29a.ch/sandbox/2012/terrain/'},
            {title: 'Normal Mapping', content: 'http://www.ro.me/tech/normal-mapping'},
            {title: 'GIS Analysis', content: 'http://webgl.uni-hd.de/realtime-WebGIS/index.html'},
            {title: 'Open Web Globe', content: 'http://swiss3d.openwebglobe.org/'},
            {title: 'Wind Patterns', content: 'http://www.senchalabs.org/philogl/PhiloGL/examples/winds/'}
        ]},
		{title: 'Video Features 3', content: [
            {title: 'Fly Over England', content: 'https://developer.mozilla.org/en-US/demos/detail/fly-over-england'},
            {title: 'Know Your Exit', content: 'http://www.robmorrismusic.com/knowyourexit/'},
            {title: 'Arms Globe', content: 'http://workshop.chromeexperiments.com/projects/armsglobe/'},
            {title: '3D Stat Map', content: 'https://developer.mozilla.org/en-US/demos/detail/3d-statistical-map'},
            {title: 'Codecademy', content: 'http://www.codecademy.com/#!/exercises/0'},
            {title: 'Khan Academy', content: 'http://www.khanacademy.org/'},
            {title: 'Radiohead Video', content: 'http://www.youtube.com/watch?v=oLrsguw1Zac'}
        ]} // TODO: Remember to ask Mike about "grey link" attributions.
	]},
	{id: "assorted", display: "none", content: [
		{id: "java_&_opengl", title: "Java & OpenGL", content: "http://www.opengl.org/resources/bindings/"},
		{id: "dependencies", title: "Dependencies", content: "http://en.wikipedia.org/wiki/Dependency_hell"},
        {id: "coupling", title: "Coupling", content: "TODO"},
		{id: "teamup", title: "TeamUp", content: "http://www.getteamup.com"},
		{id: "boot_to_gecko", title: "Boot to Gecko", content: "http://www.mozilla.org/en-US/b2g/"},
        {id: "firefox_os", title: "Firefox OS", content: "http://www.digitaltrends.com/mobile/firefox-os-can-mozilla-move-to-mobile-phones/For"},
        {id: "kinect_hacks", title: "Kinect Hacks", content: "http://www.kinecthacks.com/"},
        {id: "gis", title: "GIS", content: "http://en.wikipedia.org/wiki/Geographic_information_system"},
        {id: "processing_js", title: "Processing.js", content: "http://processingjs.org/"},
        {id: "3d_conferencing", title: "3D Conferencing", content: "https://mozillaignite.org/ideas/323/"},
        {id: "radiohead_webgl", title: "RADIOHEAD WebGL", content: "http://www.youtube.com/watch?v=oLrsguw1Zac"},
        {id: "radiohead_source", title: "(Source)", content: "http://asalga.wordpress.com/2011/09/02/house-of-cards-webgl-demo-source/"},
        {id: "glass_skull", title: "Glass Skull", content: "http://www.webgl.com/2012/02/webgl-demo-glass-skull/"},
        {id: "3d_graphics_math", title: "3D Graphics Math", content: "http://download.blender.org/documentation/bc2004/David_Cobas/m3d.pdf"},
        {id: "big_blue_button", title: "Big Blue Button", content: "http://www.bigbluebutton.org/"},
        {id: "focus_areas", title: "Focus Areas", content: "https://mozillaignite.org/apps/list/"},
        {id: "p2pu", title: "Peer 2 Peer U", content: "https://p2pu.org/en/"},
        {id: "khan_academy", title: "Khan Academy", content: "http://www.khanacademy.org/"},
        {id: "the_gig", title: "&quot;The Gig&quot;", content: "http://chattanoogagig.com/"},
        {id: "webgl_exercise", title: "WebGL Exercise", content: "TODO"},
        {id: "andors_submission", title: "Andor's Entry", content: "https://mozillaignite.org/ideas/323/"}
	]}
];