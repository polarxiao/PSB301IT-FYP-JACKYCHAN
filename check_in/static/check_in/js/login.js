


$(document).ready(function() {
    // to auto focus
    $('input:visible').first().focus();
    
    // to enable disable button
    $('#id_reservation_no').keyup();

});


$('.datepicker').datepicker({
    startDate: new Date(),
});


if ($('#id_check_in_date').val() == '') {
    $('#id_check_in_date').datepicker('update', new Date());
}


$('#id_reservation_no, #id_check_in_date').keyup(function() {
    enableDisableButton();
});


$('#id_check_in_date').datepicker().on('changeDate', function() {
    enableDisableButton();
});

function enableDisableButton() {
    $reservationNo = $('#id_reservation_no')
        , $checkInDate = $('#id_check_in_date');

    if ($reservationNo.val() != '' && $checkInDate.val() != '') {
		$('#btn-step-next').attr('disabled', false);
	} else {
		$('#btn-step-next').attr('disabled', true);
    }
}
