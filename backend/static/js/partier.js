

window.addEventListener("load", () => {
  getNationalShares();
  getCoaltionResults();
  setupSperregrense();
});


function getRGBA(Rval, Gval, Bval) {
  return "rgba(" + Rval + "," + Gval + "," + Bval + "," + "1.0)"
}

async function setupSperregrense() {

  let data = await fetch('/partier_sperregrense', {
    method: "GET",
    headers: {
      'Content-Type': 'application/json'
    }
  }).then(response => {
    return response.json();
  })
  
  
      //Setter opp dataserier
      let dataseries = {
        labels: [],
        datasets: []
      }

      for (const [partyName, partyData] of Object.entries(data)) {

        dataseries.labels = partyData['dates'];
        dataseries['datasets'].push({
           label: partyName,
           data: partyData['dataseries'],
           fill: false,
           backgroundColor: getRGBA(partyData['colors']['R'],partyData['colors']['G'],partyData['colors']['B']),
           borderColor: getRGBA(partyData['colors']['R'],partyData['colors']['G'],partyData['colors']['B']),
           tension: .1,
        })
        
      }
      
      const myChart = new Chart("sperregrenseCanvas", {
          type: 'line',
          data: dataseries,
          options: {
             responsive: true,
             maintainAspectRatio: false,
             scales: {
               x: {
                 stacked: false,
               },
               y: {
                 stacked: false,
                 min: 0,
                 max: 100,
               }
             }
           }
      });
      
    

}

//Datoer
function getDatesList() {

  //Getting
  return fetch('/simulation_dates', {
    method: "GET",
    headers: {
      'Content-Type': 'application/json'
    }
  }).then(response => {
    return response.json();
  })
}

async function getDates() {
  let dateList = await getDatesList();
  return dateList;
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


//Koalisjoner
function getCoalitionList() {

  //Getting
  return fetch('/getCoalitions', {
    method: "GET",
    headers: {
      'Content-Type': 'application/json'
    }
  }).then(response => {
    return response.json();
  })
}

async function getCoalitions() {
  let list = await getCoalitionList();
  return list;
}

//Simuleringsinfo
function getSimInfoList() {

  //Getting
  return fetch('/getSimInfo', {
    method: "GET",
    headers: {
      'Content-Type': 'application/json'
    }
  }).then(response => {
    return response.json();
  })
}

async function getSimInfo() {
  let list = await getSimInfoList();
  return list;
}


async function getNationalShares() {

  let parties = await getParties();
  let districts = await getDistricts();


  //Datoer
  let dates = [];
  let simInfo = await getSimInfo();
  for (var i = 0; i < simInfo.length; i++) {
    dates.push(simInfo[i]['date']);
  }

  let resp = fetch(`/resultater_parti_national`, {
    method: 'GET',
    headers: {
    "Content-type": "application/json; charset=UTF-8"
      }
    })
    .then((response) => response.json())
    .then(json => {
      //console.log(json);

      let labels = [];
      let datesLables = [];
      let data = {};
      let k = 0

      //Setter opp array som skal fylles
      for (const [key, value] of Object.entries(parties)) {
        data[key] = [];
      }
      //Legger over i arrays til chart
      for (var i = 0; i < json.length; i++){
        for (var j = 0; j < Object.keys(parties).length; j ++ ){
          data[j + 1].push(json[i][j+1]['shares']);
        }
        datesLables.push(i);
        labels.push(k);
        k += 1;
      }

      //Setter opp dataserier
      let dataseries = {
        labels: dates,
        datasets: []
      }

      for (const [key, value] of Object.entries(parties)) {

        dataseries['datasets'].push({
           label: parties[key]['Name'],
           data: data[key],
           fill: false,
           backgroundColor: getRGBA(parties[key]['R'],parties[key]['G'],parties[key]['B']),
           borderColor: getRGBA(parties[key]['R'],parties[key]['G'],parties[key]['B']),
           tension: .1,
        })
      }

      const myChart = new Chart("partyShare", {
          type: 'line',
          data: dataseries,
          options: {
             responsive: true,
             maintainAspectRatio: false,
             scales: {
               x: {
                 stacked: false,
               },
               y: {
                 stacked: false,
                 min: 0,
                 max: 35,
               }
             }
           }
      });
    });
}

async function getCoaltionResults() {

  let parties = await getParties();
  let coalitions = await getCoalitionList();


  //Datoer
  let dates = [];
  let simInfo = await getSimInfo();
  for (var i = 0; i < simInfo.length; i++) {
    dates.push(simInfo[i]['date']);
  }

  let resp = fetch(`/resultater_kaolisjon_national`, {
    method: 'GET',
    headers: {
    "Content-type": "application/json; charset=UTF-8"
      }
    })
    .then((response) => response.json())
    .then(json => {
      //console.log(json);

      let labels = [];
      let datesLables = [];
      let data = {};
      let data_prob = {};
      let k = 0
      let r, g, b;

      //Setter opp array som skal fylles
      for (const [key, value] of Object.entries(coalitions)) {
        data[key] = [];
        data_prob[key] = [];
      }

      //Legger over i arrays til chart
      for (var i = 0; i < json.length; i++){
        for (var j = 0; j < Object.keys(coalitions).length; j ++ ){
          data[json[i][j+1]['navn']].push(json[i][j+1]['mandater']);
          data_prob[json[i][j+1]['navn']].push(json[i][j+1]['prob']);
        }
        datesLables.push(i);
        labels.push(k);
        k += 1;
      }


      //Setter opp dataserier
      let dataseries = {
        labels: dates,
        datasets: []
      }

      let dataseries_prob = {
        labels: dates,
        datasets: []
      }

      for (const [key, value] of Object.entries(coalitions)) {

        r = Math.floor(Math.random() * 255);
        g = Math.floor(Math.random() * 255);
        b = Math.floor(Math.random() * 255);

        dataseries['datasets'].push({
           label: key,
           data: data[key],
           fill: false,
           backgroundColor: getRGBA(r,g,b),
           borderColor: getRGBA(r,g,b),
           tension: .1,
        })

        dataseries_prob['datasets'].push({
           label: key,
           data: data_prob[key],
           fill: false,
           backgroundColor: getRGBA(r,g,b),
           borderColor: getRGBA(r,g,b),
           tension: .1,
        })
        
      }

      //console.log(dataseries);

      const myChart = new Chart("coalitionMandater", {
          type: 'line',
          data: dataseries,
          options: {
             responsive: true,
             maintainAspectRatio: false,
             scales: {
               x: {
                 stacked: false,
               },
               y: {
                 stacked: false,
                 min: 0,
                 max: 110,
               }
             }
           }
      });


      //coalitionSannsynlighet
      const myChartProb = new Chart("coalitionSannsynlighet", {
          type: 'line',
          data: dataseries_prob,
          options: {
             responsive: true,
             maintainAspectRatio: false,
             scales: {
               x: {
                 stacked: false,
               },
               y: {
                 stacked: false,
                 min: 0,
                 max: 100,
               }
             }
           }
      });

    

    });

}
