
function msToTime(time_mils) {
    /**
     * convert a time in milliseconds to H:i:s
     * @param time_mils int : time in milliseconds
     */
    var hrs, secs, mils, tmp_secs, tmp_mins;

    mils = time_mils % 1000;
    tmp_secs = (time_mils - mils) / 1000;
    secs = tmp_secs % 60;
    tmp_mins = (tmp_secs - secs) / 60;
    mins = tmp_mins % 60;
    hrs = (tmp_mins - mins) / 60;
    return  hrs.toString().padStart(2, '0') + ':' +
            mins.toString().padStart(2, '0') + ':' +
            secs.toString().padStart(2, '0');
    }

function myTimer(ARG_V) {
    /**
     * update a dom element content with time data to actual value
     * element must have a value attribute with initial time reference in seconds
     * @param ARG_V : json formatted data
     *      @param id string : id of the element
     */
    var now = new Date();
    if($('#'+ARG_V.id).data('value').toString().trim() != ''){
        var start = new Date(parseInt($('#'+ARG_V.id).data('value')));
        t = now-start;
        $('#'+ARG_V.id).html(msToTime(t));
        }
    }

function value_change(event) {
    /**
     * Update a DOM element value setting a new one or adding a change quote
     * event.data param
     *  @param id_val   str : id of the element with value
     *  @param change   int : value to add
     *  @param [act_mode] str : {set}: set value of id_val, [add]: add value to id_val
     *  @param [val_min] int : minimum value
     *  @param [val_max] int : maximum value
     */
    event.data.act_mode = event.data.act_mode == undefined ? 'set' : event.data.act_mode;
    val_actual = $('#'+event.data.id_val).val().trim();
    if(event.data.act_mode == 'add'){
        var qty = $('#'+event.data.id_val).val().trim();
        if (!qty) {
            qty = 0;
            }
        qty = parseInt(qty) + event.data.change;
        }
    else{
        qty = parseInt(event.data.change);
        }
    if(event.data.val_max != undefined)
        qty = parseInt(event.data.val_max) > qty ? qty : parseInt(event.data.val_max);
    if(event.data.val_min != undefined)
        qty = parseInt(event.data.val_min) < qty ? qty : parseInt(event.data.val_min);
    $('#'+event.data.id_val).val(qty);
    }
