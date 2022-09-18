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

