
window.addEventListener("load", () => {

  let resp = fetch(`/resultater_part_mandater`, {
    method: 'POST',
    body: JSON.stringify({
      district: 2
    }),
    headers: {
      "Content-type": "application/json; charset=UTF-8"
    }
  })
  .then((response) => response.json())
  .then(json => {
    //console.log(json);
  })

  //-----------------------------------------------
  //Valgbutton distrikt
  //-----------------------------------------------

  //Legger til addEventListener paa valgbutton
  const chooseDistrict = document.getElementById("chooseDistrict");

  //Oppsett av knapp
  const districtList = document.createElement("div");
  districtList.classList.add("dropdown-menu");
  districtList.setAttribute("aria-labelledby","chooseDistrict");

  const dropdownMenu = document.getElementById("dropdownDistrict");
  dropdownMenu.appendChild(districtList);

  //Setter inn distrikter fra databasen
  let respDistricts = fetch(`/getDistricts`, {
    method: 'GET',
    headers: {
    "Content-type": "application/json; charset=UTF-8"
      }
    })
    .then((response) => response.json())
    .then(json => {

      for (const [key, value] of Object.entries(json)) {
        let district = document.createElement("a");
        district.classList.add("dropdown-item");
        district.setAttribute("href","#");
        district.innerHTML = value;
        districtList.appendChild(district);
        district.addEventListener("click", function(e) {

          chooseDistrict.innerText = this.innerText;
          updateSinglePartyCounts(key);
          updateSinglePartyCountsTimeSeries(key);
          updateCandidatesTable(key);

        });

      }
    })

    updateSinglePartyCounts(1);
    updateSinglePartyCountsTimeSeries(1);
    updateCandidatesTable(1);



    //chooseDistrict.addEventListener("click", function(e){]

/*
<div class="dropdown-menu" aria-labelledby="chooseDistrict">
  <a class="dropdown-item" href="#">Action</a>
  <a class="dropdown-item" href="#">Another action</a>
  <a class="dropdown-item" href="#">Something else here</a>
</div>

*/



});

function getRGBA(Rval, Gval, Bval) {
  return "rgba(" + Rval + "," + Gval + "," + Bval + "," + "1.0)"
}


//------------------------------------------------
//Funksjonalitet for å hente partier og fylker
//------------------------------------------------

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


async function updateSinglePartyCounts(district) {

  let parties = await getParties();
  let districts = await getDistricts();

  //Resetter Chart
  var graphContainer = document.getElementById("mandaterPerPartiDiv");
  graphContainer.innerHTML = '<canvas id="mandaterPerParti" style="width:100%;max-width:1000px"></canvas>';

  //Getting
  let resp = fetch(`/resultater_part_mandater`, {
    method: 'POST',
    body: JSON.stringify({
      district: district
    }),
    headers: {
      "Content-type": "application/json; charset=UTF-8"
    }
  })
  .then((response) => response.json())
  .then(json => {

    let labels = [];
    let data = {'Utjevningsmandater': [], 'Distriktsmandater': []}

    //Henter data
    for (const [key, value] of Object.entries(json)) {
      labels.push(parties[key]['Name']);
      data['Utjevningsmandater'].push(value['utjevning']);
      data['Distriktsmandater'].push(value['distrikt']);
    }

    //
    const dataseries = {
      labels: labels,
      datasets: [
        {
          label: 'Utjevningsmandater',
          data: data['Utjevningsmandater'],
          backgroundColor: "rgba(182, 203, 189,1.0)",
        },
        {
          label: 'Distriktsmandater',
          data: data['Distriktsmandater'],
          backgroundColor: "rgba(203, 163, 92,1.0)",
        }
      ]
    };

    const myChart = new Chart("mandaterPerParti", {
        type: 'bar',
        data: dataseries,
        options: {
           scales: {
             x: {
               stacked: true,
             },
             y: {
               stacked: true,
               min: 0,
               max: 7,
             }
           }
         }
    });
  })
}


async function updateSinglePartyCountsTimeSeries(district) {

  let parties = await getParties();
  let districts = await getDistricts();

  //Resetter Chart
  var graphContainer = document.getElementById("mandaterPerPartiOverTidDiv");
  graphContainer.innerHTML = '<canvas id="mandaterPerPartiOverTid" style="height: 500px; width:100%;max-width:1200px"></canvas>';

  let resp = fetch(`/resultater_part_mandater_time_series`, {
    method: 'POST',
    body: JSON.stringify({
      district: district
    }),
    headers: {
      "Content-type": "application/json; charset=UTF-8"
    }
  })
  .then((response) => response.json())
  .then(json => {


    let labels = [];
    let datesLables = [];
    let data = {};
    let k = 0

    //Setter opp array som skal fylles
    for (const [key, value] of Object.entries(parties)) {
      data[key] = [];
    }

    //Gjøres om til et json i js, ikke dict
    json = [json];

    //Sorterer data etter dato
    json.sort(function(a, b){
      return a.SimuleringsID - b.SimuleringsID;
    });

    //Henter ut selve jsonen
    json = json[0];

    //Legger over i arrays til chart
    for (var i = 0; i < json.length; i++){
      for (var j = 0; j < Object.keys(parties).length; j ++ ){
        //console.log(j,json[i]['Data'][j + 1]['total']);
        data[j + 1].push(json[i]['Data'][j + 1]['total']);


      }
      datesLables.push(json[i]['Dato']);
      labels.push(k);
      k += 1;
    }

    //Setter opp dataserier
    let dataseries = {
      labels: datesLables,
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
         tension: 0.1,
         pointRadius: 1,
      })
    }


    const myChart = new Chart("mandaterPerPartiOverTid", {
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
               max: 7,
             }
           }
         }
    });


  })

}


function candidateTableRow(data) {

  let resp = '<tr>'
  resp += "<td>" + data['Navn'] + '</td>'
  resp += "<td>" + data['Parti'] + '</td>'
  resp += "<td>" + data['Prob'] + '</td>'
  resp += "</tr>"

  return resp

  /*
  <tr>
    <td >Alfreds Futterkiste</td>
    <td>Maria Anders</td>
    <td>100 %</td>
  </tr>
  */

}


async function updateCandidatesTable(district) {

  let parties = await getParties();
  let districts = await getDistricts();

  console.log(parties);

  let resp = fetch(`/resultater_part_mandater_prob` , {
    method: 'POST',
    body: JSON.stringify({
      district: district
    }),
    headers: {
      "Content-type": "application/json; charset=UTF-8"
    }
  })
  .then((response) => response.json())
  .then(json => {

    //Henter data og sorterer
    sortedJson = [];
    for (const [key, value] of Object.entries(json)) {
      for (k = 0; k < value.length; k++) {
        sortedJson.push({'Navn': value[k]['Navn'], 'Prob': value[k]['P'], 'Parti': key});
      }

    }

    sortedJson.sort(function(a, b){
      return b.Prob -  a.Prob;
    });

    let table = document.getElementById("candidateListCounty");
    table.innerHTML = "";
    let htmlTable = "<tr><th>Navn</th><th>Parti</th><th>Total (%)</th></tr>";

    for (var i = 0; i < sortedJson.length; i++) {
      htmlTable += candidateTableRow(sortedJson[i]);

    }

    table.innerHTML = htmlTable;

  })

}

/*


const xValues = [50,60,70,80,90,100,110,120,130,140,150];
const xValues2 = [10,10,170,180,190,1100,110,130,140,150,160];
const yValues = [7,8,8,9,9,9,10,11,14,14,15];


const data = {
labels: xValues,
datasets: [{
    label: 'en',
    fill: false,
    lineTension: 0,
    backgroundColor: "rgba(0,0,255,1.0)",
    borderColor: "rgba(0,0,255,0.1)",
    data: yValues
  },{
      label: 'to',
      fill: false,
      lineTension: 0,
      backgroundColor: "rgba(0,0,255,1.0)",
      borderColor: "rgba(0,0,255,0.1)",
      data: xValues2
  }]
};

const myChart = new Chart("myChart", {
    type: 'line',
    data: data,
    options: {
        scales: {
            y: {
                beginAtZero: true
            }
        }
    }
});

*/
