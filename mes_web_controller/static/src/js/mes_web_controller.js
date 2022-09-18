/* timer */
function msToTime(s) {
    function pad(n, z) {
        z = z || 2;
        return ('00' + n).slice(-z);
        };

    var ms = s % 1000;
    s = (s - ms) / 1000;
    var secs = s % 60;
    s = (s - secs) / 60;
    var mins = s % 60;
    var hrs = (s - mins) / 60;
    return pad(hrs) + ':' + pad(mins) + ':' + pad(secs);
    }

function myTimer() {
    var now = new Date();
    if($("#timer").data('value').trim() != ''){
        var start = new Date(parseInt($("#timer").data('value')));
        t = now-start;
        $("#timer").html(msToTime(t));
        }
    }
