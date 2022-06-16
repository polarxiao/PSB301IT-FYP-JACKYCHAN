$('.datepicker').datepicker();
var isMainGuest = JSON.parse($('#is-main-guest').text() || '""');


$('.btn-ocr').click(function() {
    $('#id_is_submit').attr('checked', false);
});


$('#btn-back').click(function() {
	var modal =
		'<div class="modal fade" id="modal-confirmation" data-backdrop="static" data-keyboard="false" tabindex="-1" role="dialog" aria-hidden="true">' +
            '<div class="modal-dialog modal-dialog-centered modal-sm">'+
                '<div class="modal-content">'+
                    '<div class="modal-header">'+
                        '<div class="modal-title mx-auto" id="modal-label-{{ forloop.counter0 }}">'+ gettext('Warning') +'</div>'+
                    '</div>'+
                    '<div class="modal-body">'+ gettext('All changes is not saved yet. Are you sure want to do this?') +'</div>'+
                    '<div class="modal-footer justify-content-center">'+
                        '<a href="'+ $(this).data('target') +'" class="btn btn-outline-primary">'+ gettext('Yes') +'</a>'+
                        '<button type="button" class="btn btn-primary" data-dismiss="modal">'+ gettext('No') +'</button>'+
                    '</div>'+
                '</div>'+
            '</div>'+
		'</div>';
    $('.wrapper').append(modal);
    $('.modal:last').modal('show').addClass('shown');
});

