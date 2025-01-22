
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

      for (var i = 0; i < json.length; i++){
        for (var j = 0; j < json[i].length; j++) {
          console.log(i + j);
          data[i+1].push(json[i][j]['shares']);
        }
      }

      /*
      const dataseries = {
        labels: probabilities,
        datasets: [
          {
            label: 'Sannsynlighet for Stortingsplass',
            data: probabilities,
            backgroundColor: "red",
          }
        ]
      };

      const myChart = new Chart("candidateProbabilites", {
          type: 'line',
          data: dataseries,
          options: {
             scales: {
               y: {
                 min: 0,
                 max: 100,
               }
             }
           }
      });

    */

    });


}
