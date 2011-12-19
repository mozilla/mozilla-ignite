/**
 * @requires ignite.data
 * @returns {String} string of a URL that we can load in VIA xhr
 */
ignite.media_url = function(loc) {
    var id = ignite.data;
    return id.MEDIA_URL + 'ignite/' + loc + '?build=' + id.JS_BUILD_ID;
};
/**
 * Object containing file resourced for the site and specific paages
 */
ignite.areas = {
    common : [
        {
            elm : 'form.browserid_form',
            requires : 'https://browserid.org/include.js',
            onload : function() {
                var form = $('form.browserid_form');
                form.find('a.login').bind('click', function(e) {
                    e.preventDefault();
                    navigator.id.getVerifiedEmail(function(assertion) {
                        var $e = form.find('input.id_assertion');
                        $e.val(assertion.toString());
                        $e.parent().submit();
                    });
                });
            }
        }
    ],
    show_submission : {
        requires : ignite.media_url('js/include/voting.js'),
        onload : function() {
            ignite.up_votes.init();
        }
    }
};
/* Initing the sites global JavaScript */
$(function() {
    ignite.lacky  = lacky(ignite.data, ignite.areas);
    ignite.lacky.prepare();
});
