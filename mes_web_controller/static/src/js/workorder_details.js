function value_change(event) {
    /**
     * event.data param
     *  @param id_act   str : id of the element that manage value
     *  @param id_val   str : id of the element with value
     *  @param val      int : value to add
     *  @param [act_mode] str : {set}: set value of id_val, [add]: add value to id_val
     */
    event.data.act_mode = event.data.act_mode == undefined ? 'set' : 'add';
    if(event.data.act_mode == 'add'){
        var qty = $('#'+event.data.id_val).val().trim();
        if (!qty) {
            qty = 0;
            }
        qty = parseInt(qty) + event.data.val;
        }
    else{
        qty = parseInt(event.data.val);
        }

    $('#'+event.data.id_val).val(qty);
    }


function qty_ok_plus() {
    var qty = document.getElementById("qty_ok").value;
    if (!qty) {
        qty = 0;
        }
    qty = parseInt(qty);
    qty +=1;
    document.getElementById("qty_ok").value = qty;
    }

function qty_ok_minus() {
    var qty = document.getElementById("qty_ok").value;
    if (!qty) {
        qty = 0;
        }
    else {
        qty = parseInt(qty);
        qty -=1;
        if (qty < 0) {
            qty = 0
            }
        }
    document.getElementById("qty_ok").value = qty;
    }

function qty_ko_plus() {
    var qty = document.getElementById("qty_ko").value;
    if (!qty) {
        qty = 0;
        }
    qty = parseInt(qty);
    qty +=1;
    document.getElementById("qty_ko").value = qty;
    }

function qty_ko_minus() {
    var qty = document.getElementById("qty_ko").value;
    if (!qty) {
        qty = 0;
        }
    else {
        qty = parseInt(qty);
        qty -=1;
        if (qty < 0) {
            qty = 0
            }
        }
    document.getElementById("qty_ko").value = qty;
    }

