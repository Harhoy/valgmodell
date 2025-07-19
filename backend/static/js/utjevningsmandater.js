

window.addEventListener('load', async () => {

      const response = await fetch(`/getUtjevningsmandater`, {
      method: 'GET',
      headers: {
      "Content-type": "application/json; charset=UTF-8"
        }
      });
      
      const json = await response.json();
      let table = document.getElementById("utjevningsmandaterTableProb");
      let tableTxt = "<thead><tr><th>Parti</th><th>Fylke</th><th>Prob</th></tr></thead>";
      for (let i = 0; i < json.length; i ++ ) {
        console.log(json[i]);
        tableTxt += await utjevningsmandatRow(json[i]);
      }
      table.innerHTML = tableTxt;

});



async function utjevningsmandatRow(data) {

  let resp = '<tr>'
  resp += "<td>" + data['Parti'] + '</td>' 
  resp += "<td>" + data['Fylke'] + '</td>' 
  resp += "<td>" + data['Prob'].toFixed(0) + '</td>'
  resp += "</tr>"
  return resp
}

