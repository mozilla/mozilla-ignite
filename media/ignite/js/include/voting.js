ignite.up_votes = function() {
    var init;
    init = function() {
        var form = $('#user_vote'),
            text_values = {
                up: {
                    url_suffix:"up",
                    input_txt:"Give this a thumbs up",
                    input_cls:"thumb cta do"
                },
                clear:{
                    url_suffix:"clear",
                    input_txt:"Clear my vote",
                    input_cls:"cancel cta do"
                }
            };
        form.bind('submit', function() {
            var action, csrf, trigger;
            action = form.attr('action');
            csrf = form.find('input[name="csrfmiddlewaretoken"]').attr('value');
            trigger = form.find('input.cta');
            $.ajax({
                type:"POST",
                dataType:"json",
                url:action,
                data:"csrfmiddlewaretoken=" + csrf,
                success:function(data) {
                    if (trigger.is('.thumb')) {
                        obj = text_values.clear;
                    } else {
                        obj = text_values.up;
                    }
                    form.css('visibility','hidden');
                    $('span.score').html(data.score.num_votes);
                    form.find('.cta').attr({
                        'value' : obj.input_txt,
                        'class' : obj.input_cls
                    });
                    form.attr('action',action.replace(/[a-z]{2,5}$/,obj.url_suffix));
                    form.css('visibility','');
                    $('span.total_votes').html(data.score.num_votes);
                }
            });
            return false;
        });
    };
    return {
        'init': init
    };
}();
ignite.up_votes.init();
