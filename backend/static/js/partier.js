

function getRGBA(Rval, Gval, Bval) {
  return "rgba(" + Rval + "," + Gval + "," + Bval + "," + "1.0)"
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

window.addEventListener("load", () => {
  getNationalShares();
  getCoaltionResults();
});


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
          //console.log(json[i][j+1]['shares']);
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
           borderWidth: 2,
           tension: .1,
           pointRadius: 1,
        })
      }

      //console.log(dataseries);

      const myChart = new Chart("partyShare", {
          type: 'line',
          data: dataseries,
          options: {
             scales: {
               x: {
                 stacked: false,
               },
               y: {
                 stacked: false,
                 min: 0,
                 max: 30,
               }
             }
           }
      });
    });
}

async function getCoaltionResults() {

  let parties = await getParties();
  let coalitions = await getCoalitionList();


  console.log(coalitions);

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
      let k = 0

      //Setter opp array som skal fylles
      for (const [key, value] of Object.entries(coalitions)) {
        data[key] = [];
      }

      //Legger over i arrays til chart
      for (var i = 0; i < json.length; i++){
        for (var j = 0; j < Object.keys(coalitions).length; j ++ ){
          console.log(json[i][j+1]['navn']);
          data[json[i][j+1]['navn']].push(json[i][j+1]['mandater']);
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

      for (const [key, value] of Object.entries(coalitions)) {

        dataseries['datasets'].push({
           label: key,
           data: data[key],
           fill: false,
           backgroundColor: getRGBA(coalitions[key]['R'],coalitions[key]['G'],coalitions[key]['B']),
           borderColor: getRGBA(coalitions[key]['R'],coalitions[key]['G'],coalitions[key]['B']),
           borderWidth: 2,
           tension: .1,
           pointRadius: 1,
        })
      }

      //console.log(dataseries);

      const myChart = new Chart("coalitionMandater", {
          type: 'line',
          data: dataseries,
          options: {
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

    });

}
