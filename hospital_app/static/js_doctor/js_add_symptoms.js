
var counter3 = 1;
function addSymptoms(divName){
        var newdiv = document.createElement('div');
          newdiv.innerHTML = "Symptom " + (counter3 + 1) + "<input type='text' name='symptoms_inputs[]' required = 'required'>";
          document.getElementById(divName).appendChild(newdiv);
          counter3++;
}
