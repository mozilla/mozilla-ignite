ignite.link_node_manager.content[0] = {
    notes: "This is the global group of non-link_node objects.",
    content: [
        {notes: "The Ignite logo", time_in: 40, time_out: 43,
            start: function (){
                var logo1 = document.getElementById("logo1");
                logo1.className = "centered_logo";
                logo1.style.display = "block";
                logo1.style.opacity = "0"
                logo1.transition       = "left 2s, top 1s, opacity 1s, height 1s, width 1s";
                logo1.MozTransition    = "left 2s, top 1s, opacity 1s, height 1s, width 1s";
                logo1.WebkitTransition = "left 2s, top 1s, opacity 1s, height 1s, width 1s";
                logo1.OTransition      = "left 2s, top 1s, opacity 1s, height 1s, width 1s";
                setTimeout(function (){
                    logo1.style.opacity = "1";
                }, 100);
                if(!this.setup){
                    this.setup = true;
                    ignite.popcorn.cue(this.time_in+1, function (){
                        logo1.className = "positioned_logo";
                    })
                }
            },
            end: function (){
                var logo1 = document.getElementById("logo1");
                logo1.transition       = " ";
                logo1.MozTransition    = " ";
                logo1.WebkitTransition = " ";
                logo1.OTransition      = " ";
                logo1.style.display = "block";
                logo1.style.opacity = "1";
                logo1.className = "positioned_logo";
                },
            check: function (time_code){
                var logo1 = document.getElementById("logo1");
                if(time_code < this.time_in){
                    logo1.className = "centered_logo";
                    logo1.style.display = "none";
                    logo1.style.opacity = "0";
                } else if(time_code > this.time_out){
                    this.end();
                }
            }
        },
        {notes: "The WebGL logo", time_in: 42, time_out: 45,
            start: function (){
                var logo2 = document.getElementById("logo2");
                logo2.className = "centered_logo";
                logo2.style.display = "block";
                logo2.transition       = "right 2s, top 1s, opacity 1s, height 1s, width 1s";
                logo2.MozTransition    = "right 2s, top 1s, opacity 1s, height 1s, width 1s";
                logo2.WebkitTransition = "right 2s, top 1s, opacity 1s, height 1s, width 1s";
                logo2.OTransition      = "right 2s, top 1s, opacity 1s, height 1s, width 1s";
                setTimeout(function (){
                    logo2.style.opacity = "1";
                }, 100);
                if(!this.setup){
                    this.setup = true;
                    ignite.popcorn.cue(this.time_in+1, function (){
                        logo2.className = "positioned_logo";
                    })
                }
            },
            end: function (){
                var logo2 = document.getElementById("logo2");
                logo2.transition       = " ";
                logo2.MozTransition    = " ";
                logo2.WebkitTransition = " ";
                logo2.OTransition      = " ";
                logo2.style.display = "block";
                logo2.style.opacity = "1";
                logo2.className = "positioned_logo";
                },
            check: function (time_code){
                var logo2 = document.getElementById("logo2");
                if(time_code < this.time_in){
                    logo2.className = "centered_logo";
                    logo2.style.display = "none";
                    logo2.style.opacity = "0";
                } else if(time_code > this.time_out){
                    this.end();
                }
            }
        },
        {notes: "Walkthrough", time_in: 44, time_out: 52,
            displayed: undefined, // Needed for unexpected behavior in Chrome.
            start: function (){
                if(this.displayed){ return;}
                this.displayed = true;
                var walkthrough_button = document.getElementById("walkthrough_link");
                walkthrough_button.style.display = "block";
                if(!this.setup){
                    this.setup = true;
                    var passed_event = this;
                    walkthrough_button.addEventListener("click", function (){
                        ignite.start_walkthrough();
                        passed_event.end();
                    });
                }
                /* The following setTimeout call is necessary to prevent
                 * block and opacity from being set simultaneously, which would
                 * result in a spontaneous appearance instead of a fade-in.
                 */
                if(this.timeout_id){
                    clearTimeout(this.timeout_id);
                }
                this.timeout_id = setTimeout((function (passed_button){
                    return function (){
                        passed_button.style.opacity = "1";
                    }
                })(walkthrough_button), 1000);
            },
            end: function (){
                if(!this.displayed){ return;}
                this.displayed = false;
                var walkthrough_button = document.getElementById("walkthrough_link");
                walkthrough_button.style.opacity = "0";
                if(this.timeout_id){
                    clearTimeout(this.timeout_id);
                }
                this.timeout_id = setTimeout((function (passed_button){
                    return function (){
                        passed_button.style.display = "none";
                    }
                })(walkthrough_button), 1000);
            },
            check: function (time_code){
                if(time_code > this.time_in && time_code < this.time_out){
                    this.start();
                } else{
                    this.end();
                }
            }
        },
        {notes: "Add Arrows", time_in: 55, time_out: 56,
            started: undefined, // Needed for unexpected behavior in Chrome.
            start: function (){
                if(this.started){ return;}
                this.started = true;
                setTimeout(function (){
                    ignite.arrow_left.style.opacity  = "1";
                    ignite.arrow_right.style.opacity = "0";
                }, 100);
            },
            end: function (){},
            check: function (time_code){
                if(time_code >= this.time_in){
                    this.start();
                }
            }
        },
        {notes: "Credits", time_in: 557, time_out: 600,
            displayed: undefined, // Needed for unexpected behavior in Chrome.
            start: function (){
                if(this.displayed){ return;}
                this.displayed = true;
                var credits_button = document.getElementById("credits_link");
                credits_button.style.display = "block";
                if(!this.setup){
                    this.setup = true;
                    var passed_event = this;
                    credits_button.addEventListener("click", function (){
						ignite.transition("right", true);
                        passed_event.end();
                    });
                }
                /* The following setTimeout call is necessary to prevent
                 * block and opacity from being set simultaneously, which would
                 * result in a spontaneous appearance instead of a fade-in.
                 */
                if(this.timeout_id){
                    clearTimeout(this.timeout_id);
                }
                this.timeout_id = setTimeout((function (passed_button){
                    return function (){
                        passed_button.style.opacity = "1";
                    }
                })(credits_button), 1000);
            },
            end: function (){
                if(!this.displayed){ return;}
                this.displayed = false;
                var credits_button = document.getElementById("credits_link");
                credits_button.style.opacity = "0";
                if(this.timeout_id){
                    clearTimeout(this.timeout_id);
                }
                this.timeout_id = setTimeout((function (passed_button){
                    return function (){
                        passed_button.style.display = "none";
                    }
                })(credits_button), 1000);
            },
            check: function (time_code){
                if(time_code > this.time_in && time_code < this.time_out){
                    this.start();
                } else{
                    this.end();
                }
            }
        }
    ]
};













