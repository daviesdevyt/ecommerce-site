function locate(loc){
    window.location.href = '/'+loc
}

function addtocart(id)
{
    fetch('/add-to-cart', {
        method: "POST",
        body: JSON.stringify({product_id: id})
    }).then((_res) => {
        locate('')
    })
}

function removefromcart(id)
{
    fetch('/remove-from-cart', {
        method: "POST",
        body: JSON.stringify({product_id: id})
    }).then((_res) => {
        locate('cart')
    })
}


function changequantity(id, op)
{
    fetch('/edit-quantity', {
        method: "POST",
        body: JSON.stringify({product_id: id, operation: op})
    }).then((_res) => {
        locate('cart')
    })
}



var modal = document.getElementById("checkoutModal");

var btn = document.getElementById("checkoutModalbtn");

var span = document.getElementsByClassName("close")[0];

btn.onclick = function() {
  modal.style.display = "block";
}

span.onclick = function() {
  modal.style.display = "none";
}

window.onclick = function(event) {
  if (event.target == modal) {
    modal.style.display = "none";
  }
}