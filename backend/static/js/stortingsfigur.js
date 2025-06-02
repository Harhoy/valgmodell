

window.addEventListener('load', async () => {

  // Initial graph
  drawGraph(-2);

  //Button declarations
  let button = document.getElementById("nasjonal-prognose");
  button.addEventListener('click', function() {
    drawGraph(-2);
  });

  button = document.getElementById("regional-prognose");
  button.addEventListener('click', function() {
    drawGraph(-1);
  });

});

async function drawGraph(id) {

  let intialData = await get_storting(id);
  let parties = Array(Object.keys(intialData[0]).length);
  let hs = Array(Object.keys(2).length);
  let dagens = Array(Object.keys(3).length);


  hs[0] = {'Name': "Venstresiden", 'Mandater': 0 , 'HEX': "#EE4B2B", 'shares': 0};
  hs[1] = {'Name': "Høyresiden", 'Mandater': 0 , 'HEX': "#0000FF", 'shares': 0};

  dagens[0] = {'Name': "Regjeringsgrunnlag", 'Mandater': 0 , 'HEX': "#ffa500", 'shares': 0};
  dagens[1] = {'Name': "Opposisjonen", 'Mandater': 0 , 'HEX': "#808080", 'shares': 0};
  
  let data, lr, name, hex, share, seats;
  for (let i = 0; i < Object.keys(intialData[0]).length; i++) {
    data = intialData[0][i+1];
    lr = data['LR'];
    hex = data['hex'];
    name = data['name'];
    seats = data['seats'];
    shares = data['shares'];
    parties[lr] = {'Name': name, 'Mandater': seats , 'HEX': hex, 'shares': shares.toFixed(1)};    

    if (lr < 5) {
      hs[0]['Mandater'] += seats;
      hs[0]['shares'] += shares;
    } else {
      hs[1]['Mandater'] += seats;
      hs[1]['shares'] += shares;    
    }

    if (name === "A" || name === "SV" || name === "SP") {
      dagens[0]['Mandater'] += seats;
      dagens[0]['shares'] += shares;
    } else {
      dagens[1]['Mandater'] += seats;
      dagens[1]['shares'] += shares;
    }
  }

     

  updateGraph(parties, "partyCanvas");
  updateGraph(hs, "hsCanvas");
  updateGraph(dagens, "dagensCanvas");
  updatePartyTable(parties);
  updateFylkesTable(parties, id);

  
}


async function updateFylkesTable(parties, id) {

  // Regional og nasjonal
  let result = await getSeatsPerCounty(id);
  let districts = await getDistricts();
  
  
    let table = document.getElementById("fylkesTableTotalt");
    let tableDirekte = document.getElementById("fylkesTableDirekte");
    let tableUtjevning = document.getElementById("fylkesTableUtjevning");

    
    htmlTableTotal = "<tr> <th> Fylke </th>";
    htmlTableDirekte= "<tr> <th> Fylke </th>";
    htmlTableUtjevning= "<tr> <th> Fylke </th>";
    
    for (var i = 0; i < parties.length; i++) {
      htmlTableTotal += "<th>" + parties[i]['Name'] + "</th>";
      htmlTableDirekte += "<th>" + parties[i]['Name'] + "</th>";
      htmlTableUtjevning += "<th>" + parties[i]['Name'] + "</th>";
    }
    htmlTableTotal += "</tr>";
    htmlTableDirekte += "</tr>";
    htmlTableUtjevning += "</tr>";
    //table.innerHTML = htmlTable

    for (const [fylke, navn] of Object.entries(districts)) { 

      htmlTableTotal +=  "<tr>" + "<td>" + navn + "</td>";
      htmlTableDirekte +=  "<tr>" + "<td>" + navn + "</td>";
      htmlTableUtjevning +=  "<tr>" + "<td>" + navn + "</td>";
      
      for (var party = 0; party < parties.length; party++) {
        let p = parties[party]['Name'];
        let total = parseFloat(result[fylke-1][p]['Utjevningsmandater']) + parseFloat(result[fylke-1][p]['Distriktsmandater']);

        
        console.log(p + " " + total);

        htmlTableTotal += "<td>" + total + '</td>'
        htmlTableDirekte += "<td>" + parseFloat(result[fylke-1][p]['Distriktsmandater']) + '</td>'
        htmlTableUtjevning += "<td>" + parseFloat(result[fylke-1][p]['Utjevningsmandater']) + '</td>'
      }
      htmlTableTotal += "</tr>";
      htmlTableDirekte += "</tr>";
      htmlTableUtjevning += "</tr>";

    }

    table.innerHTML = htmlTableTotal;
    tableDirekte.innerHTML = htmlTableDirekte;
    tableUtjevning.innerHTML = htmlTableUtjevning;
    
}

function resultater_national_specific(id) {
    return fetch('/resultater_national_specific', {
    method: "POST",
    body: JSON.stringify({
      simID: id
    }),
    headers: {
      'Content-Type': 'application/json'
    }
    }).then(response => {
      return response.json();
    })        
}

async function get_storting(id) {
  let storting = await resultater_national_specific(id);
  return storting;
}

async function updateGraph(parties, name) {

  //canvas
  let canvas = document.getElementById(name);
  let ctx = canvas.getContext("2d");
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  let newGraph = new ElectoralChart(name, parties, true);
  
}


async function updatePartyTable(parties) {
    let table = document.getElementById("partyTable");
    table.innerHTML = "";
    let htmlTable = "<tr><th>Parti</th><th>Mandater</th><th>Stemmeandel (%)</th></tr>";
    for (var i = 0; i < parties.length; i++) {
      htmlTable += partyRow(parties[i]);
    }
    table.innerHTML = htmlTable;
}


async function getSeatsPerCounty(simID) {

  let parties = await getParties();
  let response = [];

  for (let i = 0; i < 19; i++) {
  
      //Getting
      let resp = await fetch(`/resultater_part_mandater`, {
        method: 'POST',
        body: JSON.stringify({
          district: i + 1,
          simID: simID
        }),
        headers: {
          "Content-type": "application/json; charset=UTF-8"
        }
      })
      .then((response) => response.json())
      .then(json => {

        let labels = [];
        let data = {}

        //Henter data
        for (const [key, value] of Object.entries(json)) {
          labels.push(parties[key]['Name']);
          data[parties[key]['Name']] = {'Utjevningsmandater': [value['utjevning']], 'Distriktsmandater': [value['distrikt']]}
          }

        //console.log(data);
        return data;
          
        }) 

        response.push(resp);
  
  }

  return response;


}


function partyRow(data) {
  let resp = '<tr>'
  resp += "<td>" + data['Name'] + '</td>'
  resp += "<td>" + data['Mandater'] + '</td>'
  resp += "<td>" + data['shares'] + '</td>'
  resp += "</tr>"
  return resp
}



//Partier
function getPartyList() {

  //Getting
  return fetch('/getParties', {
    method: "GET",
    headers: {
      'Content-Type': 'application/json'
    }
  }).then(response => {
    return response.json();
  })
}

async function getParties() {
  let partyList = await getPartyList();
  return partyList;
}

//Fylker
function getDistrictList() {

  //Getting
  return fetch('/getDistricts', {
    method: "GET",
    headers: {
      'Content-Type': 'application/json'
    }
  }).then(response => {
    return response.json();
  })
}

async function getDistricts() {
  let list = await getDistrictList();
  return list;
}

