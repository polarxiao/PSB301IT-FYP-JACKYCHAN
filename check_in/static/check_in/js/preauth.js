$('#form-preauth').card({
    form: 'form',
    container: '.card-wrapper',
    formSelectors: {
        numberInput: 'input#id_card_no',
        nameInput: 'input#id_card_username',
        expiryInput: 'input#id_card_expiry',
        cvcInput: 'input#id_card_code',
    },
    placeholders: {
        number: '**** **** **** ****',
        name: 'John Smith',
        expiry: 'MM/YYYY',
        cvc: '123'
    }
});


