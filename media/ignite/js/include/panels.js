ignite.panels = function() {
    var init;
    init = function() {
        var triggers = $('h2.trigger'),
            open,
            open_trigger;
        triggers.each(function(index) {
            var that = $(this),
                btn = $('<button class="box" tab-index="-1">' + that.text() + ' <span class="inst">(click to expand)</span></button>'),
                nxt = that.next('div.panel');
            that.html(btn);
            if (index === 0) {
                nxt.addClass('open-panel');
                btn.addClass('open-panel');
                open = nxt;
                open_trigger = btn;
            }
            btn.click(function() {
                open.removeClass('open-panel');
                open_trigger.removeClass('open-panel');
                nxt.addClass('open-panel');
                btn.addClass('open-panel');
                open = nxt;
                open_trigger = btn;
                open_trigger.focus();
            });
        });
    };
    return {
        'init': init
    };
}();
