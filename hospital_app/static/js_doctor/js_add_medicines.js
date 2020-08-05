
var counter1 = 1;
function addMedicines(divName){
        var newdiv = document.createElement('div');
          newdiv.innerHTML = "Medicine " + (counter1 + 1) + "<input type='text' name='medicines_inputs[]' required = 'required'>";
          document.getElementById(divName).appendChild(newdiv);
          counter1++;
}
