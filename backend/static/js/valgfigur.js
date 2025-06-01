







//Dummy tall
let parties = [{'Name': 'Rødt', 'Mandater': 9, 'HEX': '#6b1f20'},
              {'Name': 'SV', 'Mandater': 12, 'HEX': '#ba4c59'},
              {'Name': 'MDG', 'Mandater': 2, 'HEX': '#4cba55'},
              {'Name': 'Arbeiderpartiet', 'Mandater': 45, 'HEX': '#eb4034'},
              {'Name': 'Senterpartiet', 'Mandater': 10, 'HEX': '#3ca305'},
              {'Name': 'KrF', 'Mandater': 4, 'HEX': '#f5f107'},
              {'Name': 'Venstre', 'Mandater': 8, 'HEX': '#4cbaa6'},
                {'Name': 'Høyre', 'Mandater': 60, 'HEX': '#325aa8'},
              {'Name': 'FrP', 'Mandater': 5, 'HEX': '#9b34eb'}];

//Graph
let graph = new ElectoralChart("myCanvas", parties);

const button = document.getElementById("calcBtn");
button.addEventListener('click', () => updateGraph());

const dwnldBtn = document.getElementById("dwnldBtn");
dwnldBtn.addEventListener('click', () => downloadImage());

window.addEventListener('load', () => {
  for (let i = 0; i < parties.length; i++) {
    document.getElementById(parties[i]['Name'] + "Input").value = parties[i]['Mandater'].toString();
  }
});


function updateGraph() {

  //canvas
  let canvas = document.getElementById("myCanvas");
  let ctx = canvas.getContext("2d");
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  for (let i = 0; i < parties.length; i++) {
    parties[i]['Mandater'] = parseInt(document.getElementById(parties[i]['Name'] + "Input").value);
  }

  let newGraph = new ElectoralChart("myCanvas", parties);

  console.log(parties);

}


function downloadImage() {

  let canvas = document.getElementById("myCanvas");
  let link = document.createElement('a');
  link.download = "stortingsgrafikk.png";
  link.href = canvas.toDataURL('image/png');
  link.click();

}
