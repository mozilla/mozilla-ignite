ignite.idea_links = function() {
    var links = $('fieldset.external_links'),
        add_link_set;
    add_link_set = function() {
        var add_link = $('<a href="#" class="add_link">Add another link</a>').appendTo(links),
            total_links = $('#id_externals-TOTAL_FORMS');
        add_link.click(function() {
            var rows = links.find('div.inline_field'),
                index = rows.length,
                dupe = $(rows[0]).clone();
            dupe.find('label, input').map(function() {
                var that = $(this),
                    id_val = that.attr('id'),
                    name_val = that.attr('name'),
                    for_val = that.attr('for');
                if (name_val) {
                    that.attr({
                        'name': name_val.replace(/\d/g, index),
                        'id': id_val.replace(/\d/g, index),
                        'value': ''
                    });
                } else {
                    that.attr('for', for_val.replace(/\d/g, index));
                }
            });
            total_links.attr('value', index + 1);
            dupe.insertBefore(add_link);
            dupe.find('input:first').focus();
            return false;
        });
    };
    return {
        'add_link_set': add_link_set
    };
}();
