
const partyList = ['Ap', 'Frp','H', 'KrF','MDG','R','SP','SV','V'];

const partyListLookup = {'Arbeiderpartiet':1, 'Fremskrittspartiet':2,'Høyre':3, 'Kristelig folkeparti':4,'Miljøpartiet de Grønne':5,'Rødt':6,'Senterpartiet':7,'Sosialistisk Venstreparti':8,'Venstre':9};

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

        });

      }
    })

    updateSinglePartyCounts(1);
    updateSinglePartyCountsTimeSeries(1);



    //chooseDistrict.addEventListener("click", function(e){]

/*
<div class="dropdown-menu" aria-labelledby="chooseDistrict">
  <a class="dropdown-item" href="#">Action</a>
  <a class="dropdown-item" href="#">Another action</a>
  <a class="dropdown-item" href="#">Something else here</a>
</div>

*/



});


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
      labels.push(parties[key]);
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
  graphContainer.innerHTML = '<canvas id="mandaterPerPartiOverTid" style="height: 500px; width:100%;max-width:1000px"></canvas>';

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
      labels.push(k);
      k += 1;
    }

    //Setter opp dataserier
    let dataseries = {
      labels: labels,
      datasets: []
    }

    for (const [key, value] of Object.entries(parties)) {
      dataseries['datasets'].push({
         label: parties[key],
         data: data[key],
         fill: false,
         tension: 0.1
      })
      //console.log(data[key])
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
