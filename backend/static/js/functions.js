
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

export async function getSimInfo() {
  let list = await getSimInfoList();
  return list;
}

function testModules() {
  return "hei";  
}



export{testModules};
