// do not compress more than declared below, otherwise canvas will be blank
// https://github.com/jhildenbiddle/canvas-size
var maxCanvasWidth = 4096, maxCanvasHeight = 4096;
// accepted file type on uploading
var acceptedFileType = ['jpg', 'jpeg', 'png'];
// compressor options, for compressing captured and uploaded image
Compressor.setDefaults({
    mimeType: 'image/png',
    maxWidth: 1050,
    maxHeight: 800,
    convertSize: 2000000,
});
// croppie options, for scaling and rotating captured and uploaded image
// var croppieOpts = {
//     viewport: { width: 320, height: 240 },
//     boundary: { width: 427, height: 320 },
//     showZoomer: true,
//     enableOrientation: true,
// };
var croppieOpts = {
    viewport: { width: 340, height: 240 },
    boundary: { width: 375, height: 494 },
    showZoomer: true,
    enableOrientation: true,
};
$('#img-preview').croppie(croppieOpts); // init croppie to element, use `bind` to add image data


// btn-upload click
$('.file-upload').change(function() {
    var file = event.target.files[0]
        , isInitial = $('.croppie-container #text-preview').length == 0;

    if (file === undefined) modalAlert(gettext('Invalid Image'), gettext('No image file selected'));
    if (!validateFileType($(this).val())) modalAlert(gettext('Invalid Image'), gettext('Please upload valid identification in JPEG/PNG format'));
    new Compressor(file, {
        success: function(result) {
            blobToDataURL(result, function(dataURL) {
                $('#img-preview').croppie('bind', dataURL).then(function() { // update image data
                    $('#img-preview').croppie('setZoom', 0); // change zoom level
                });
                if (isInitial) { // will not init if re-upload or re-take
                    initCroppieComponents();
                    initBorderGuide();
                }
            });
        },
        error: function(err) {
            console.error('Compressor() error:'+ err.message);
            modalAlert(gettext('Error'), gettext('Error capturing image'));
        },
    });
});


// btn-webcam click
$('#btn-webcam').click(function() {
    var video = document.getElementById('vid-webcam')
        , mediaConfig =  { video: true }
        , errorConsole = function(error) {
            console.error('getUserMedia() error:', error);
            modalAlert(gettext('Error'), gettext('No camera media is detected'));
        };
    
    // Put video listeners into place
    if(navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia(mediaConfig).then(function(stream) {
            video.srcObject = stream;
            video.play();
            $('.default-container, #btn-skip').hide();
            $('.webcam-container').show();
        });
    }

    /* Legacy code below! */
    else if(navigator.getUserMedia) { // Standard
        navigator.getUserMedia(mediaConfig, function(stream) {
            video.src = stream;
            video.play();
            $('.default-container, #btn-skip').hide();
            $('.webcam-container').show();
        }, errorConsole);
    } else if(navigator.webkitGetUserMedia) { // WebKit-prefixed
        navigator.webkitGetUserMedia(mediaConfig, function(stream){
            video.play();
            $('.default-container, #btn-skip').hide();
            $('.webcam-container').show();
        }, errorConsole);
    } else if(navigator.mozGetUserMedia) { // Mozilla-prefixed
        navigator.mozGetUserMedia(mediaConfig, function(stream){
            video.play();
            $('.default-container, #btn-skip').hide();
            $('.webcam-container').show();
        }, errorConsole);
    }
});


// btn-capture click
$('#btn-capture').click(function() {
    var video = document.getElementById('vid-webcam')
        , stream = video.srcObject
        , tracks = stream.getTracks()
        , $img = $('#img-preview')
        , draw = document.createElement('canvas')
        , context2D = draw.getContext('2d');
        
    draw.width = video.videoWidth;
    draw.height = video.videoHeight;
    context2D.drawImage(video, 0, 0, video.videoWidth, video.videoHeight);
    // stop video
    tracks.forEach(function(track) { track.stop(); });
    new Compressor(dataURLtoBlob(draw.toDataURL('image/png')), {
        success: function(result) {
            blobToDataURL(result, function(dataURL) {
                $img.croppie('bind', dataURL).then(function() { // update image data
                    $img.croppie('setZoom', 0); // change zoom level
                });
                initCroppieComponents();
                initBorderGuide();
            });
        },
        error: function(err) {
            console.error('Compressor() error:'+ err.message);
            modalAlert(gettext('Error'), gettext('Error capturing image'));
        },
    });
});


// btn-next click
$('#btn-next').click(function() {
    var $img = $('#img-preview')
        , $ocrFile = $('#id_ocr_file')
        , dataURL;

    $img.croppie('result', {
        'type': 'rawcanvas',
        'size': 'original',
        'format': 'png',
    }).then(function(canvas) {
        dataURL = canvas.toDataURL();
        $ocrFile.val(dataURL.substring(22)); // remove `data:image/png;base64,` on dataURL
        $('#form-ocr').submit();
    });
});


// validate file type
function validateFileType(fileName) {
    var splited = fileName.split('.')
        , fileType = (splited[splited.length - 1]).toLowerCase();
    if ((!fileName) || (splited.length <= 1) || (acceptedFileType.indexOf(fileType) < 0)) return false;
    return true;
}


// blob to dataURL
function blobToDataURL(blob, callback) {
    var reader = new FileReader();
    reader.onload = function(e) { callback(e.target.result); }
    reader.readAsDataURL(blob);
}


// dataURL to blob
function dataURLtoBlob(dataURL) {
    var arr = dataURL.split(','), mime = arr[0].match(/:(.*?);/)[1],
        bstr = atob(arr[1]), n = bstr.length, u8arr = new Uint8Array(n);
    while(n--){
        u8arr[n] = bstr.charCodeAt(n);
    }
    return new Blob([u8arr], {type:mime});
}


// initiate croppie components, ie: moving timer, add rotate button, etc
function initCroppieComponents() {
    var $previewText = $('<div></div>').addClass('text-white').attr('id', 'text-preview').html(gettext('Please adjust the image to make sure<br>that all information is within the box.'))
        , $zoomWrap
        , $zoomWord = $('<div></div>').addClass('text-white text-center').html(gettext('Zoom'))
        , $iconRotate = $('<span></span>').addClass('material-icons-outlined').text('rotate_90_degrees_ccw')
        , $btnRotate = $('<button></button>').attr('type', 'button').addClass('btn btn-dark').attr('id', 'btn-rotate').data('degree', 90).html($iconRotate).click(function () {
            $('#img-preview').croppie('rotate', $(this).data('degree'));
        })
        , $rotateContainer = $('<div></div>').attr('id', 'rotate-container').append($btnRotate);

    $('.page-header, .page-subheader, .default-container, .webcam-container').hide();
    $('.cr-slider-wrap').appendTo('.croppie-container'); // move back to prevent error on `croppie('destroy')`
    $('.preview-container, #btn-skip').show();
    $zoomWrap = $('.cr-slider-wrap');
    $zoomWord.prependTo($zoomWrap);
    $('.cr-boundary').append($previewText, $zoomWrap, $rotateContainer);
}


// initiate border guide on croppie view port
function initBorderGuide() {
    var guideTopRight1 = $('<div></div>').addClass('guide-top-right-1')
        , guideTopRight2 = $('<div></div>').addClass('guide-top-right-2')
        , guideBottomRight1 = $('<div></div>').addClass('guide-bottom-right-1')
        , guideBottomRight2 = $('<div></div>').addClass('guide-bottom-right-2')
        , guideTopLeft1 = $('<div></div>').addClass('guide-top-left-1')
        , guideTopLeft2 = $('<div></div>').addClass('guide-top-left-2')
        , guideBottomLeft1 = $('<div></div>').addClass('guide-bottom-left-1')
        , guideBottomLeft2 = $('<div></div>').addClass('guide-bottom-left-2')

    $('.cr-boundary .cr-viewport').append(
        guideTopRight1,
        guideTopRight2,
        guideBottomRight1,
        guideBottomRight2,
        guideTopLeft1,
        guideTopLeft2,
        guideBottomLeft1,
        guideBottomLeft2
    );
}
