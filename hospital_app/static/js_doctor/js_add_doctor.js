
var counter = 1;
function addDoctor(divName){
        var newdiv = document.createElement('div');
          newdiv.innerHTML = "Doctor " + (counter + 1) + " <br><input type='text' name='doctor_inputs[]' required = 'required'>";
          document.getElementById(divName).appendChild(newdiv);
          counter++;
}
