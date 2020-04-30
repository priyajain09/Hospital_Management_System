
var counter2 = 1;
function addReports(divName){
        var newdiv = document.createElement('div');
          newdiv.innerHTML = "Report " + (counter2 + 1) + "<input type='text' name='reports_inputs[]'>";
          document.getElementById(divName).appendChild(newdiv);
          counter2++;
}
