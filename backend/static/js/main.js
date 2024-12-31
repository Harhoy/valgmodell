
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
    console.log(json);
  })

  //Legger til addEventListener paa valgbutton
  const chooseDistrict = document.getElementById("chooseDistrict");
  //chooseDistrict.addEventListener("click", function(e){]

  const districtList = document.createElement("div");
  districtList.classList.add("dropdown-menu");
  districtList.setAttribute("aria-labelledby","chooseDistrict");

  const dropdownMenu = document.getElementById("dropdownDistrict");
  dropdownMenu.appendChild(districtList);

  for (const [key, value] of Object.entries(partyListLookup)) {
    console.log(key);
  }

/*
<div class="dropdown-menu" aria-labelledby="chooseDistrict">
  <a class="dropdown-item" href="#">Action</a>
  <a class="dropdown-item" href="#">Another action</a>
  <a class="dropdown-item" href="#">Something else here</a>
</div>

*/



});



//<canvas id="myChart" style="width:100%;max-width:700px"></canvas>

function addPlotSinglePartyCounts(countVector) {


}


function chooseDistrictClick(){

}


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
