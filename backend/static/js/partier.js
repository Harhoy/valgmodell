
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
      console.log(json);

      let labels = [];
      let data = {};

      for (const [key, value] of Object.entries(json[0])) {
        data[key] = [];
      }

      for (var i = 0; i < json.length-1; i++){
        for (var j = 0; j < 9; j++) {
          //console.log(i , j,json[i][j+1]);
          data[j+1].push(json[i][j+1]['shares']);
        }
      }

      console.log(data);


      const dataseries = {
        labels: data[1],
        datasets: [
          {
            label: 'Sannsynlighet for Stortingsplass',
            data: data[2],
            backgroundColor: "red",
          }
        ]
      };

      const myChart = new Chart("partyShare", {
          type: 'line',
          data: dataseries,
          options: {
             scales: {
               y: {
                 min: 0,
                 max: 30,
               }
             }
           }
      });



    });


}
