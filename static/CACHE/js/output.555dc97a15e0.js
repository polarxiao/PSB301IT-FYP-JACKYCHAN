$('body').addClass('loading');$(window).on('load',function(){$('body').removeClass('loading');$('.modal.auto-show').each(function(){if(!$('body').hasClass('modal-open')){$(this).modal('show').addClass('shown');}
$(this).on('hidden.bs.modal',function(e){$('.modal.auto-show:not(.shown)').first().modal('show').addClass('shown');});});});$('form').submit(function(){if(!$('body').hasClass('live'))$('body').addClass('loading');});$(document).on({ajaxStart:function(){if(!$('body').hasClass('live'))$('body').addClass('loading');},ajaxStop:function(){$('body').removeClass('loading');}});$('.toast').toast('show');$('.multiple-choice input[type=checkbox]').change(function(){if($(this).prop('checked')){$(this).parents('label.choice').addClass('selected');}else{$(this).parents('label.choice').removeClass('selected');}});function modalAlert(title=gettext('Error'),body=gettext('Error'),btnDismissText=gettext('Close')){var modal='<div class="modal fade" data-backdrop="static" data-keyboard="false" tabindex="-1" role="dialog" aria-hidden="true">'+'<div class="modal-dialog modal-dialog-centered modal-sm">'+'<div class="modal-content">'+'<div class="modal-header">'+'<div class="modal-title mx-auto" id="modal-label-{{ forloop.counter0 }}">'+title+'</div>'+'</div>'+'<div class="modal-body">'+body+'</div>'+'<div class="modal-footer">'+'<button type="button" class="btn btn-primary mx-auto" data-dismiss="modal">'+btnDismissText+'</button>'+'</div>'+'</div>'+'</div>'+'</div>';$('.wrapper').append(modal);$('.modal:last').modal('show').addClass('shown');};;$('#form-preauth').card({form:'form',container:'.card-wrapper',formSelectors:{numberInput:'input#id_card_no',nameInput:'input#id_card_username',expiryInput:'input#id_card_expiry',cvcInput:'input#id_card_code',},placeholders:{number:'**** **** **** ****',name:'John Smith',expiry:'MM/YYYY',cvc:'123'}});;