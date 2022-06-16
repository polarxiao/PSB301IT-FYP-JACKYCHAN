// event when reservation thumbnail is clicked
$('.thumbnail-container').click(function() {
    $(this).find('input').prop('checked', true).change();
    $('#form-reservation').submit();
});
