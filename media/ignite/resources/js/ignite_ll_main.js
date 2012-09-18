/*
 * This code written in whole by Jacob A Brennan.
 *
 * This work is licensed under the Creative Commons Attribution 3.0 Unported
 * License. To view a copy of this license, visit
 * http://creativecommons.org/licenses/by/3.0/ or send a letter to Creative
 * Commons, 444 Castro Street, Suite 900, Mountain View, California, 94041, USA.
 */

ignite = {
    setup: function (){
        this.seeking = false;
        this.popcorn = Popcorn("#webgl_lab");
        window.addEventListener("resize", function (){ ignite.resize()}, false);
        window.addEventListener("keydown", function (e){ ignite.key_down(e);}, false);
        // Configure Custom Controls:
        var controls = document.getElementById("controls");
            // Play/Pause Button
        var play_button = document.getElementById("control_play")
        play_button.addEventListener("click", function (){
            if(ignite.popcorn.currentTime() == ignite.popcorn.duration()){
                ignite.popcorn.currentTime(0);
                ignite.popcorn.play();
                return;
            }
            if(ignite.popcorn.paused()){ ignite.popcorn.play();}
            else{ ignite.popcorn.pause();}
        }, false);
        this.popcorn.on("playing", function (){
            play_button.getElementById("play" ).style.opacity = "0";
            play_button.getElementById("pause").style.opacity = "1";
        });
        this.popcorn.on("pause", function (){
            var play_button = document.getElementById("control_play")
            play_button.getElementById("play" ).style.opacity = "1";
            play_button.getElementById("pause").style.opacity = "0";
        });
        this.popcorn.on("ended", function (){
            var play_button = document.getElementById("control_play")
            play_button.getElementById("play" ).style.opacity = "1";
            play_button.getElementById("pause").style.opacity = "0";
        });
            // Progress Bar and Timer
        var progress_bar = document.getElementById("control_progress");
        var buffered_bar = document.getElementById("control_buffered_time");
        var elapsed_bar = document.getElementById("control_elapsed_time");
        var timer = document.getElementById("control_timer");
        progress_bar.addEventListener("click", function (event){
            var duration = ignite.popcorn.duration();
            if(!duration){ return;}
            var resized_width = progress_bar.clientWidth;
            var actual_left = 0;
            var offset_element = progress_bar;
            while(offset_element){
                actual_left += offset_element.offsetLeft;
                offset_element = offset_element.offsetParent;
            }
            var click_percent = (event.clientX-actual_left) / resized_width;
            var seek_time = duration * click_percent;
            elapsed_bar.style.width = ""+(click_percent*100)+"%";
            ignite.popcorn.currentTime(seek_time);
        });
        this.popcorn.on("timeupdate", function (){
            var duration = ignite.popcorn.duration();
            if(!duration){ return;}
            var current_time = ignite.popcorn.currentTime();
            var elapsed_percent = current_time / duration;
            elapsed_bar.style.width = ""+(elapsed_percent*100)+"%";
            var extra_0 = ((current_time%60) < 10)? "0" : "";
            current_time = ""+Math.floor(current_time/60)+":"+extra_0+Math.floor(current_time%60);
            var timer_text = timer.getElementById("svg_timer");
            if(ignite.current_duration){
                timer_text.textContent = ""+current_time+"/"+ignite.current_duration;
            } else{
                timer_text.textContent = ""+current_time;
            }
        });
        this.popcorn.on("progress", function (){
            ignite.current_duration = ignite.popcorn.duration();
            if(!ignite.current_duration){ return;}
            var buffered_range = ignite.popcorn.buffered();
            var buffer_end = buffered_range.end(0);
            if(!buffer_end){ buffer_end = 0}
            buffered_bar.style.width = ""+((buffer_end/ignite.current_duration)*100)+"%";
            var current_time = ignite.popcorn.currentTime()
            var extra_0 = ((current_time%60) < 10)? "0" : "";
            current_time = ""+Math.floor(current_time/60)+":"+extra_0+Math.floor(current_time%60);
            ignite.current_duration = ""+Math.floor(ignite.current_duration/60)+":"+Math.floor(ignite.current_duration%60);
            var timer_text = timer.getElementById("svg_timer");
            if(ignite.current_duration){
                timer_text.textContent = ""+current_time+"/"+ignite.current_duration;
            } else{
                timer_text.textContent = ""+current_time;
            }
        });
            // Volume:
        var mute_button = document.getElementById("control_mute");
        mute_button.addEventListener("click", function (){
            if(ignite.popcorn.muted()){
                ignite.popcorn.unmute();
                mute_button.getElementById("sound" ).style.opacity = "1";
            } else{
                ignite.popcorn.muted(true);
                mute_button.getElementById("sound" ).style.opacity = "0";
            }
        }, false);
        // Prevent Fullscreen:
        this.popcorn.media.requestFullScreen = function (){ return false;};
        this.popcorn.media.mozRequestFullScreen = function (){ return false;};
        document.addEventListener("webkitfullscreenchange", function () {
            document.webkitCancelFullScreen();
        }, false);
        // Setup frame slider:
        this.frame = document.getElementById("frame");
        this.slider = document.getElementById("slider");
        this.middle = document.getElementById("video_content");
        this.right  = document.getElementById("community" );
        this.left   = document.getElementById("resources"  );
        this.video_width = 1280;
        this.video_height = 720;
        this.slider_state = "middle";
        this.arrow_left  = document.getElementById("arrow_left" );
        this.arrow_right = document.getElementById("arrow_right");
        this.arrow_left.addEventListener("click", function (){
            ignite.transition("left");
        }, false)
        this.arrow_right.addEventListener("click", function (){
            ignite.transition("right");
        }, false)
        this.resize();
        // Setup Resource Section:
        var setup_node = function (node, tier){
            for(var I = 0; I < node.content.length; I++){
                var resource = node.content[I];
                resource.tier = tier+1;
                var container_li = document.createElement("li");
                /* A separate block container is needed to prevent our resources
                 * from having an ancestor positioned absolutely. Otherwise
                 * percentage sizing would be based on that ancestor instead of
                 * the frame. */
                node.list.appendChild(container_li)
                var r_element
                var logo_text;
                if(typeof(resource.content) == "string"){
                    r_element = document.createElement("a");
                    resource.element = r_element;
                    r_element.setAttribute("id", "rsc_"+resource.title)
                    r_element.setAttribute("class", "resource tier"+(tier+1));
                    r_element.setAttribute("href", resource.content);
                    r_element.setAttribute("target", "_blank");
                    logo_text = ' link"><img src="/media/ignite/resources/svg/linkbox_padding.svg" />';
                    r_element.innerHTML = '<div class="title">'+resource.title+'</div><div class="icon'+logo_text+'</div>';
                }
                else{
                    r_element = document.createElement("div");
                    resource.element = r_element;
                    r_element.setAttribute("id", "rsc_"+resource.title)
                    r_element.setAttribute("class", "resource tier"+(tier+1));
                    r_element.addEventListener("click",
                        (function (resource_replacement){
                            return function (){
                                ignite.resources.highlight(resource_replacement);
                            }
                        })(resource),
                    false);
                    logo_text = '"><img src="/media/ignite/resources/svg/ignite_embossed_logo.svg" />';
                    r_element.innerHTML = '<div class="title">'+resource.title+'</div><div class="icon'+logo_text+'</div>';
                    resource.list = document.createElement("ul");
                    container_li.appendChild(resource.list);
                    setup_node(resource, tier+1);
                }
                container_li.appendChild(r_element);
                r_element.style.top = (20+I*10)+"%";
            }
        }
        this.resources.list = document.getElementById("resource_list");
        setup_node(this.resources, 0);
        // Setup Video Driven pop-corn elements (Global & Link Node):
        // Setup Global events:
        var global_group = this.link_node_manager.content[0];
        for(var I = 0; I < global_group.content.length; I++){
            var indexed_event = global_group.content[I];
            var indexed_start_function = (function (passed_event){
                return function (){
                    passed_event.start();
                }
            })(indexed_event);
            var indexed_end_function = (function (passed_event){
                return function (){
                    passed_event.end();
                }
            })(indexed_event);
            this.popcorn.cue(indexed_event.time_in , indexed_start_function);
            this.popcorn.cue(indexed_event.time_out, indexed_end_function  );
        }
        // Setup Link Nodes events:
        for(var I = 1; I < this.link_node_manager.content.length; I++){
            // I is set to 1 so as to skip the global list of elements at position 0.
            var group = this.link_node_manager.content[I];
            for(var group_index = 0; group_index < group.content.length; group_index++){
                var link_node = group.content[group_index];
                var cue_function = (function (indexed_node){
                    return function (){
                        if(ignite.seeking){ return;}
                        var node = ignite.link_node_manager.create_node(indexed_node);
                        var custom;
                        if(indexed_node.position){
                            custom = indexed_node.position;
                        }
                        ignite.link_node_manager.add_node(node, custom);
                    };
                })(link_node);
                this.popcorn.cue(link_node.time_in, cue_function);
            }
            this.popcorn.cue(group.time_out, function (){
                ignite.link_node_manager.clear_nodes();
            })
        }
        this.popcorn.on("seeked", function (){
            ignite.seeking = false;
            ignite.link_node_manager.setup_at(ignite.popcorn.currentTime());
        });
        this.popcorn.on("seeking", function (){
            ignite.seeking = true;
            ignite.link_node_manager.clear_nodes();
        });
        // Finished
    },
    start_walkthrough: function (){
        if(this.walkthrough_in_progress){
            return;
        }
        this.walkthrough_in_progress = true;
        // There cannot be more than one popcorn instance per document.
        ignite.popcorn.pause();
        //ignite.popcorn.emit("seeking");
        ignite.link_node_manager.clear_nodes();
        //var walkthrough = Popcorn("#walkthrough_audio");
        setTimeout(/*
        walkthrough.cue(1, */function (){
            var test_resource = {title: 'Outside Content', content: "http://example.com/"};
            var test_node = ignite.link_node_manager.create_node(test_resource);
            ignite.link_node_manager.add_node(test_node);
        }, 1000);
        setTimeout(/*
        walkthrough.cue(2, */function (){
            var test_resource = {title: 'Topic'};
            var test_node = ignite.link_node_manager.create_node(test_resource);
            ignite.link_node_manager.add_node(test_node);
        }, 2000);
        setTimeout(/*
        walkthrough.cue(3, */function (){
            var test_resource = {title: 'Outside Content', content: "http://example.com/"};
            var test_node = ignite.link_node_manager.create_node(test_resource);
            ignite.link_node_manager.add_node(test_node);
        }, 3000);
        setTimeout(/*
        walkthrough.cue(4, */function (){
            var test_resource = {title: 'Outside Content', content: "http://example.com/"};
            var test_node = ignite.link_node_manager.create_node(test_resource);
            ignite.link_node_manager.add_node(test_node);
        }, 4000);
        setTimeout(/*
        walkthrough.cue(6, */function (){
            ignite.link_node_manager.clear_nodes()
            ignite.transition("left");
            ignite.arrow_right.style.display = "none";
        }, 6000);
        setTimeout(/*
        walkthrough.cue(10, */function (){
            ignite.resources.highlight(ignite.resources.content[0]);
        }, 10000);
        setTimeout(/*
        walkthrough.on("ended", */function (){
            ignite.popcorn.currentTime(55);
            ignite.link_node_manager.setup_at(ignite.popcorn.currentTime(55))
            setTimeout(function (){
                ignite.transition("right");
                ignite.walkthrough_in_progress = false;
            }, 250);
            setTimeout(function (){
                ignite.resources.unhighlight(ignite.resources.highlight_tier1);
            }, 1000);
        }, 13000);
        var walkthrough_audio = document.getElementById("walkthrough_audio");
        walkthrough_audio.play()
    },
    viewport_size: function (){
        var e  = document.documentElement;
        var g  = document.getElementsByTagName('body')[0];
        var _x = window.innerWidth  || e.clientWidth  || g.clientWidth;
        var _y = window.innerHeight || e.clientHeight || g.clientHeight;
        return {width: _x, height: _y};
    },
    key_down: function (e){
        var key_code;
        if(window.event){ key_code = e.keyCode} // IE 8 and earlier compatibility.
        else{
            key_code = e.which// | e.keyCode;
        }
        switch(key_code){
            case 37:{
                this.transition("left");
                break;
            }
            case 39:{
                if(this.slider_state == "left"){
                    this.transition("right");
                }
                break;
            }
        }
    },
    resize: function (){
        this.slider.style.transition       = "";
        this.slider.style.MozTransition    = "";
        this.slider.style.WebkitTransition = "";
        this.slider.style.OTransition      = "";
        var size = this.viewport_size();
        var monitor_aspect_ratio = size.width / size.height;
        var video_aspect_ratio = 16 / 9;
        var modified_width;
        var modified_height;
        if(monitor_aspect_ratio >= video_aspect_ratio){
            // Center Horizontally
            modified_height = size.height;
            modified_width = video_aspect_ratio * modified_height;
            this.frame.style.top = "0px";
            this.frame.style.left = ""+Math.floor((size.width-modified_width)/2)+"px";
        } else{
            // Center Vertically
            modified_width = size.width;
            modified_height = modified_width / video_aspect_ratio;
            this.frame.style.top = ""+Math.floor((size.height-modified_height)/2)+"px";
            this.frame.style.left = "0px";
        }
        this.frame.style.width  = modified_width +"px";
        this.frame.style.height = modified_height+"px";
        this.frame.style.fontSize = Math.round(modified_height/20)+"px";
        this.left.style.fontSize = Math.round(modified_height/16)+"px";
        document.getElementById("walkthrough_link").style.fontSize = Math.round(modified_height/13)+"px";
        this.middle.style.top     = "0px";
        this.left.style.top       = "0px";
        this.right.style.top      = "0px";
        this.slider.style.top     = "0px";
        this.middle.style.left    = ( modified_width  )+"px";
        this.left.style.left      = "0px";
        this.right.style.left     = ( modified_width*2)+"px";
        switch(this.slider_state){
            case "middle":{
                this.slider.style.left = "-100%";
                break;
            }
            case "left":{
                this.slider.style.left = "0%";
                break;
            }
            case "right":{
                this.slider.style.left = "-200%"
                break;
            }
        }
        this.middle.style.width   = modified_width+"px";
        this.left.style.width     = modified_width+"px";
        this.right.style.width    = modified_width+"px";
        this.slider.style.width   = (modified_width*3)+"px";
        this.middle.style.height  = modified_height+"px";
        this.left.style.height    = modified_height+"px";
        this.right.style.height   = modified_height+"px";
        this.slider.style.height  = modified_height+"px";
    },
    transition: function (direction){
        this.slider.style.transition       = "left 1s";
        this.slider.style.MozTransition    = "left 1s";
        this.slider.style.WebkitTransition = "left 1s";
        this.slider.style.OTransition      = "left 1s";
        switch(direction){
            case "left":{
                switch(this.slider_state){
                    case "middle":{
                        this.slider_state = "left";
                        break;
                    }
                    case "right":{
                        this.slider_state = "middle";
                        break;
                    }
                }
                break;
            }
            case "right":{
                switch(this.slider_state){
                    case "middle":{
                        this.slider_state = "right";
                        break;
                    }
                    case "left":{
                        this.slider_state = "middle";
                        break;
                    }
                }
                break;
            }
        }
        switch(this.slider_state){
            case "left":{
                this.slider.style.left = "0%";
                this.arrow_left.style.opacity = "0";
                this.arrow_right.style.opacity = "1";
                this.popcorn.pause()
                break;
            }
            case "middle":{
                this.slider.style.left = "-100%";
                this.arrow_left.style.opacity = "1";
                this.arrow_right.style.opacity = "0";
                if(!this.walkthrough){
                    this.popcorn.play();
                }
                break;
            }
            case "right":{
                this.slider.style.left = "-200%";
                this.arrow_right.style.opacity = "0";
                this.popcorn.pause()
                break;
            }
        }
    },    
    link_node_manager: {
        current_nodes: new Array(),
        add_node: function (node, custom){
            ignite.middle.appendChild(node);
            if(custom){
                this.custom_node = node;
                node.style.top = custom.top;
                node.style.left = custom.left;
                node.style.transition       = "opacity 1s";
                node.style.MozTransition    = "opacity 1s";
                node.style.WebkitTransition = "opacity 1s";
                node.style.OTransition      = "opacity 1s";
            } else{
                var position;
                for(var I = 0; I < this.current_nodes.length; I++){
                    if(!this.current_nodes[I]){
                        position = I;
                        break;
                    }
                }
                if(position === undefined){
                    position = Math.min(this.current_nodes.length, 4)
                }
                if(this.current_nodes.length > position && this.current_nodes[position]){
                    this.bump_node(this.current_nodes[position]);
                }
                this.current_nodes[position] = node;
                var percent = 30 + position*8
                node.style.top = percent+"%";
                node.style.left = "7%";
                node.style.transition       = "opacity 1s, left 2s, top 1s";
                node.style.MozTransition    = "opacity 1s, left 2s, top 1s";
                node.style.WebkitTransition = "opacity 1s, left 2s, top 1s";
                node.style.OTransition      = "opacity 1s, left 2s, top 1s";
            }
            /* The following statement must be delayed from the other settings
             * to ensure that the transition happens.
             */
            setInterval(function (){node.style.opacity = "1";}, 10);
        },
        bump_node: function (node){
            node.style.transition       = "opacity 1s, left 2s, top 1s";
            node.style.MozTransition    = "opacity 1s, left 2s, top 1s";
            node.style.WebkitTransition = "opacity 1s, left 2s, top 1s";
            node.style.OTransition      = "opacity 1s, left 2s, top 1s";
            var place = this.current_nodes.indexOf(node);
            this.current_nodes[place] = null;
            place--;
            if(place < 0){
                this.remove_node(node);
            } else{
                node.style.top = 30+(8*place)+"%";
                var old_node = this.current_nodes[place];
                if(old_node){
                    this.bump_node(old_node);
                }
                this.current_nodes[place] = node;
            }
        },
        create_node: function (node_json){
            var node;
            if(node_json.content){
                node = document.createElement("a");
                node.setAttribute("href", node_json.content)
                node.setAttribute("target", "_blank");
                node.innerHTML = '<div class="title">'+node_json.title+'</span></div><div class="icon"><img src="linkbox_padding.svg" /></div>';
                
            } else{
                node = document.createElement("div");
                node.innerHTML = '<div class="title">'+node_json.title+'</span></div><div class="icon"><img src="ignite_embossed_logo.svg" /></div>';
            }
            node.setAttribute("class", "link_node");
            return node;
        },
        remove_node: function (node){
            if(node == this.custom_node){
                node.style.opacity = "0";
                this.custom_node = undefined;
            } else{
                node.style.left = "-100%";
                var position = this.current_nodes.indexOf(node);
                if(position != -1){
                    this.current_nodes[position] = undefined;
                }
            }
            setTimeout(function (){
                ignite.middle.removeChild(node);
            }, 1000);
        },
        clear_nodes: function (){
            if(this.custom_node){
                this.remove_node(this.custom_node);
            }
            for(var I = 0; I < this.current_nodes.length; I++){
                var node = this.current_nodes[I];
                if(node){
                    this.remove_node(node);
                }
            }
        },
        setup_at: function (time_code){
            // Setup Global events:
            var global_group = this.content[0];
            for(var event_index = 0; event_index < global_group.content.length; event_index++){
                var indexed_event = global_group.content[event_index];
                indexed_event.check(ignite.popcorn.currentTime());
            }
            // Setup current link node group:
            var display_group;
            var display_nodes = new Array();
            for(var I = 1 ; I < this.content.length; I++){
                // This index starts at 1 so as to skip the global group at position 0.
                var group = this.content[I];
                if(group.time_in <= time_code && group.time_out > time_code){
                    display_group = group;
                    break;
                }
            }
            if(!display_group){ return;}
            for(var node_index = display_group.content.length-1; node_index >= 0; node_index--){
                var indexed_node = display_group.content[node_index];
                if(indexed_node.time_in > time_code){
                    continue;
                }
                display_nodes.push(indexed_node);
                if(display_nodes.length >= 5){
                    break;
                }
            }
            if(display_nodes.length <= 0){ return;}
            for(var I = display_nodes.length-1; I >= 0; I--){
                var indexed_node = display_nodes[I];
                var new_node = this.create_node(indexed_node);
                var custom;
                if(indexed_node.position){
                    custom = indexed_node.position;
                }
                this.add_node(new_node, custom)
            }
        }
    }
};
ignite.resources = {
    highlight: function (resource){
        switch(resource.tier){
            case 1:{
                if(this.highlight_tier1){
                    this.unhighlight(this.highlight_tier1);
                }
                this.highlight_tier1 = resource;
                break;
            }
            case 2:{
                if(this.highlight_tier2){
                    this.unhighlight(this.highlight_tier2);
                }
                this.highlight_tier2 = resource;
                break;
            }
        }
        resource.element.firstChild.style.background = "rgb(239, 72, 25)";
        for(var I = 0; I < resource.content.length; I++){
            var sub_rsc = resource.content[I];
            var old_left = sub_rsc.element.style.left;
            var old_top = sub_rsc.element.style.top;
            sub_rsc.element.style.left = (10+((resource.tier-1)*28))+"%";
            sub_rsc.element.style.top  = resource.element.style.top;
            sub_rsc.element.style.display = "block";
            sub_rsc.element.style.transition       = "top 1s, left 0.5s";
            sub_rsc.element.style.MozTransition    = "top 1s, left 0.5s";
            sub_rsc.element.style.WebkitTransition = "top 1s, left 0.5s";
            sub_rsc.element.style.OTransition      = "top 1s, left 0.5s";
            var mover_func = (function (indexed_rsc, indexed_left, indexed_top){
                return function (){
                    indexed_rsc.element.style.left = indexed_left;
                    indexed_rsc.element.style.top = indexed_top;
                }
            })(sub_rsc, old_left, old_top)
            setTimeout(mover_func, 50);
        }
    },
    unhighlight: function (resource){
        if(resource.tier == 1){
            if(this.highlight_tier2){
                this.unhighlight(this.highlight_tier2);
            }
        }
        this["highlight_tier"+resource.tier] = null;
        resource.element.firstChild.style.background = null;
        for(var I = 0; I < resource.content.length; I++){
            var sub_rsc = resource.content[I];
            sub_rsc.element.style.display = "none";
            sub_rsc.element.style.transition       = "";
            sub_rsc.element.style.MozTransition    = "";
            sub_rsc.element.style.WebkitTransition = "";
            sub_rsc.element.style.OTransition      = "";
        }
    }
};
document.addEventListener("DOMContentLoaded", function (){
    ignite.setup();
});