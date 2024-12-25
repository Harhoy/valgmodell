

//window.addEventListener("load", () => {

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

//});
