
var counter = 1;
function addMedicines(divName){
        var newdiv = document.createElement('div');
          newdiv.innerHTML = "Medicines " + (counter + 1) + "<input type='text' name='medicines_inputs[]'>";
          document.getElementById(divName).appendChild(newdiv);
          counter++;
}
