$(function() {
    'use strict';
    // Pop a confirm dialogue on delete button submission.
    $('.confirm').submit(function() {
        if (confirm('Are you sure you want to remove this item?')) {
            return true;
        }
        return false;
    });
});
