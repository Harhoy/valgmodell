


window.addEventListener('load', async () => {

  //try {

    const response = await fetch(`/maaalingerInfo`, {
      method: 'GET',
      headers: {
      "Content-type": "application/json; charset=UTF-8"
        }
      });
      
      const json = await response.json();
      let table = document.getElementById("maalingerTable");
      let tableTxt = "<thead><tr><th>Institutt</th><th>Dato</th><th>Vekt</th><th>Antall spurte</th><th>Kilde (POP)</th></tr></thead>";
      for (let i = 0; i < json.length; i ++ ) {
        console.log(json[i]);
        tableTxt += await partyRow(json[i]);
      }
      table.innerHTML = tableTxt;
  
  //} catch {
  //  console.error("Error");
  //}
  
  


});

async function partyRow(data) {
  let resp = '<tr>'
  resp += "<td>" + data[1] + '</td>' //Institutt
  resp += "<td>" + data[4] + '</td>' //Dato
  resp += "<td>" + data[2].toFixed(3) + '</td>' //Vekt
  resp += "<td>" + data[3] + '</td>'  //Antall spurte
  resp += "<td>" + "<a href=https://www.pollofpolls.no/?cmd=Maling&gallupid=" + data[0] + "> Lenke" + "</a>"+ '</td>'  //Kilde
  resp += "</tr>"
  return resp
}



