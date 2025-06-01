
/*
---------------------------------------------
This file contains different handy functions


---------------------------------------------
*/

//Distance between two points
function distance(p1, p2) {
  return ((p1.x  - p2.x) ** 2 + (p1.y - p2.y) ** 2) ** .5;
}

//Dot product between two vectors
function dot(a1, a2) {
  var sum = 0;
  for (let i = 0; i < a1.length; i++) {
    sum += a1[i] * a2[i];
  }
  return sum;
}

//Length of a single vector
function length(a1) {
  var sum = 0;
  for (let i = 0; i < a1.length; i++) {
    sum += a1[i] ** 2;
  }
  return sum ** .5;
}

//Computes angle between two vectors
function angle(a1, a2) {
  return dot(a1, a2)/ (length(a1) * length(a2));
}

//Computes angle between two vectors where it is assumed that vector 1 gives the "north" position in the local system
function angleBaseNorth(a1, a2) {
  if ((Math.sign(a1[0]) != Math.sign(a2[0])) && (Math.sign(a1[1]) != Math.sign(a2[1]))) {
    return 2 * Math.PI - Math.acos(angle(a1,a2));
  }
  return Math.acos(angle(a1,a2));
}

//Computes the percentage of distance between 90 and 270 degress for a given angle
function leftRight(angle) {
  return (3/2 * PI - angle) / (3/2 * PI - 1/2 * PI);
}

//Draws a line on a canvas from a context, two points and a width
function drawLine(ctx, p1, p2, width) {

  ctx.beginPath();
  ctx.lineWidth = width;
  ctx.strokeStyle = "white";
  ctx.moveTo(p1.x, p1.y);
  ctx.lineTo(p2.x, p2.y);
  ctx.fill();
  ctx.stroke();
}

//Draws a node on a canvas from a context, point (with x and y attributes), radius and color
function drawNode(ctx, p, radius, color){
  ctx.beginPath();
  let x = p.x;
  let y = p.y;
  ctx.arc(x, y, radius, 0, 2 * Math.PI);
  ctx.fillStyle = color;
  ctx.fill();
  //ctx.stroke();
}


class PQ {

  constructor () {
    this.values = [];
  }

  //Gives minimim placement
  insertMin(item, priority) {

    //If it is placed within array
    let placed = false;

    //If empty
    if (this.values.length == 0) {
      this.values.push({'item': item, 'priority': priority});
      return;
    }

    //Check for dominance
    for (let i = 0; i < this.values.length; i++){
      if (priority < this.values[i]['priority']) {
        this.values.splice(i, 0, {'item': item, 'priority': priority});
        placed = true;
        break;
      }
    }

    //At the end if not placed
    if (!placed) {
      this.values.push({'item': item, 'priority': priority});
    }

  }

  //return first in list
  pop() {
    return this.values.shift();
  }

  empty(){
    if (this.values.length == 0){
      return true;
    }
    return false;
  }

}
