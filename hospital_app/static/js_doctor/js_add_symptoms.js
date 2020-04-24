
var counter = 1;
function addSymptoms(divName){
        var newdiv = document.createElement('div');
          newdiv.innerHTML = "Symptoms " + (counter + 1) + "<input type='text' name='symptoms_inputs[]'>";
          document.getElementById(divName).appendChild(newdiv);
          counter++;
}
