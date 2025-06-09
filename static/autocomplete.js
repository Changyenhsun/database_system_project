function setupAutoComplete(inputId, url, suggestionBoxId) {
    const input = $('#' + inputId);
    const box = $('#' + suggestionBoxId);

    input.on('input', function () {
        const query = $(this).val();
        if (query.length === 0) {
            box.empty().hide();
            return;
        }
        $.get(url, { q: query }, function (data) {
            box.empty();
            if (data.length > 0) {
                data.forEach(function (item) {
                    box.append(`<li>${item}</li>`);
                });
                box.show();
            } else {
                box.hide();
            }
        });
    });

    box.on('click', 'li', function () {
        input.val($(this).text());
        box.empty().hide();
    });
}

$(document).ready(function () {
    setupAutoComplete('director', '/autocomplete/director', 'director-suggestions');
    setupAutoComplete('actor', '/autocomplete/actor', 'actor-suggestions');
});
