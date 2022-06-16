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


// btn-webcam click
$('.btn-webcam').click(function() {
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
            $('.default-container, .preview-container, #btn-skip').hide();
            $('.webcam-container').show();
        });
    }

    /* Legacy code below! */
    else if(navigator.getUserMedia) { // Standard
        navigator.getUserMedia(mediaConfig, function(stream) {
            video.src = stream;
            video.play();
            $('.default-container, .preview-container, #btn-skip').hide();
            $('.webcam-container').show();
        }, errorConsole);
    } else if(navigator.webkitGetUserMedia) { // WebKit-prefixed
        navigator.webkitGetUserMedia(mediaConfig, function(stream){
            video.play();
            $('.default-container, .preview-container, #btn-skip').hide();
            $('.webcam-container').show();
        }, errorConsole);
    } else if(navigator.mozGetUserMedia) { // Mozilla-prefixed
        navigator.mozGetUserMedia(mediaConfig, function(stream){
            video.play();
            $('.default-container, .preview-container, #btn-skip').hide();
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
                $img.attr('src', dataURL);
                $('.page-header, .page-subheader, .default-container, .webcam-container').hide();
                $('.preview-container, #btn-skip').show();
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
    var imgData = $('#img-preview').attr('src')
        , imgType = imgData.substring("data:image/".length, imgData.indexOf(";base64"))
        , index = imgType == 'jpeg' ? 23 : 22
        , $frFile = $('#id_fr_file');
    
    $frFile.val(imgData.substring(index)); // remove `data:image/png;base64,` or `data:image/jpeg;base64,` on dataURL
    $('#form-fr').submit();
});


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
