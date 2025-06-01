
/*

Harald Høyem 23.03.2025
ElectionChart

please import "utils.js" in HTML before this script

*/



// ---- CONSTANTS -----
//PI
var PI = 3.14;

//Horizontal weight
//Makes sure that dots on the same angle are ordered according to distance from root node
var HORIZ_WEIGHT = 0.000000000001;

// --------------------

class ElectoralChart {

  constructor(canvasName, parties = null) {

    //canvas
    this.canvas = document.getElementById(canvasName);
    this.canvas.width = "600";
    this.canvas.height = "350";

    //Context to in which the illustrations are drawn
    this.ctx = this.canvas.getContext("2d");

    //Dict with party data
    this.parties = parties;

    //Radius of each node
    this.nodeRadius = 10;

    //Initial distance from center in graph to first row
    this.radialDistance = 100;

    //Total number of nodes to allocate
    if (parties != null) {
      this.organizeSeats()

    //Graphical debug purposes
    } else {

      //dummy value if no parties given (for debug)
      this.totalNodes = 100;
    }

    //Counting the number of nodes
    this.nodeCounter = 0;

    //Counter for how many nodes are left to place
    this.leftToPlace = this.totalNodes;

    //Inital, wanted gap between each node
    this.gap = 5;

    //List of gaps in each layer
    this.gapList = [];

    //All rows that have been placed
    this.rows = [];

    //Root node (for drawing other noded and debug purposes)
    this.rootNode = new Node(this, this.canvas.width / 2, this.canvas.width * 0.5);
    this.rootNode.color = "red";

    //Nodes sorted from left to right (by angle to root node)
    this.sortedNodes = new PQ();

    //Setup
    this.adapt();

  }

  //Reads the array with parties and sets up relevant data structures
  organizeSeats() {

    //Resetting
    this.totalNodes = 0;

    //Which party is to be placed in which seats (ordered from left to right)
    this.partyBracket = [];

    //Contains info on parties
    this.partyInfo = {}

    //Utils
    let from = null;
    let to = null;

    for (let i = 0; i < this.parties.length; i++){

      //Keep for later (kinda redundant)
      this.partyInfo[this.parties[i]['Name']] = {'Mandater': this.parties[i]['Mandater'], 'HEX': this.parties[i]['HEX']};

      //Create array with color information per seat
      from = this.totalNodes + 1;
      this.totalNodes += this.parties[i]['Mandater'];
      to = this.totalNodes;

      //Setting up color info in array
      //if (i == 0) {from -= 1;}
      for (let j = from; j <= to; j++){
          this.partyBracket.push(this.parties[i]['HEX']);
      }
    }

    //console.log(this.partyBracket);
  }

  //Function to compute the standard deviation of gap variance in each layer
  computeGapVariance() {
    let sum = 0;
    let mean = 0;
    for (let i = 0; i < this.gapList.length; i++){
      mean += this.gapList[i];
    }
    mean = mean / this.gapList.length;
    for (let i = 0; i < this.gapList.length; i++){
      sum += (mean -  this.gapList[i]) ** 2;
    }
    return (sum / this.gapList.length ** 2) ** 0.5;
  }

  //Finds the radial distance giving the smallest variation in gaps used in each layer
  adapt() {

    //Gap in current iteration
    let gap = 0.0;

    //Smallest gap found
    let minGap = 10 ** 9;

    //Distance associated with smallest gap
    let minDistance = this.radialDistance;

    //Hard coded max value (based on tests - hard coded)
    let radialDistanceMax = 150;

    //Checking for each value (line search)
    while (this.radialDistance < radialDistanceMax) {

      //Getting the gap
      gap = this.setup();

      //Skipping those that are not computable
      if (!isNaN(gap)) {
        if (gap < minGap) {
          minGap = gap;
          minDistance = this.radialDistance;
        }
      }

      //Incremtenting distance and resetting
      this.radialDistance += 1;
      this.reset();
    }

    //Implementing minimum distance and setting up with those values
    this.radialDistance = minDistance;
    this.setup();
    this.drawRows();

  }

  //Resetting the relevant data
  reset() {
    this.leftToPlace = this.totalNodes;
    this.gap = 5;
    this.rows = [];
    this.gapList = [];
    this.nodeCounter = 0;
    this.sortedNodes = new PQ();
  }

  //Drawing all rows and nodes
  setup() {

    //Setting inital radialDistance
    let radialDistance = this.radialDistance;

    //draw initial root node (debug)
    //this.rootNode.draw();

    //Create rows
    while (this.leftToPlace > 0) {

      //Setting up a new row
      let newRow = new Row(this, radialDistance);

      //Filling it with nodes
      newRow.setup(this.rows.length);

      //Updating distance to next row
      radialDistance += 2 * this.nodeRadius + this.gap;

      //Adding to rows
      this.rows.push(newRow);

    }

    //Computing the variane (or standard deviation) of the current node placement
    return this.computeGapVariance();

  }

  //Drawing all rows with party color
  drawRows() {

    let node = null;
    let k = 0;
    while (!this.sortedNodes.empty()) {
      node = this.sortedNodes.pop()['item'];
      node.color = this.partyBracket[k];
      node.draw();
      k += 1 ;
    }

  }

  //Drawing all rows in a uniform color
  drawRowsOneColor() {
    for (let i = 0; i < this.rows.length; i++){
      this.rows[i].drawNodes();
    }
  }
}

class Row {

  constructor(graph, radialDistance) {

    //Electoral graph
    this.graph = graph;

    //Distance from centerpoint to row
    this.radialDistance = radialDistance;

    //nodes in row
    this.nodes = [];

  }

  //Creating the row
  setup(number) {

    //Intial guess of nodes that will fit within layer
    let nodesLocal = Math.floor(1 + (this.radialDistance * PI) / (2 * this.graph.nodeRadius + this.graph.gap));

    //Checking if there are more nodes left to place
    nodesLocal = Math.min(this.graph.leftToPlace, nodesLocal);

    //Updating the number of nodes left to place
    this.graph.leftToPlace -= nodesLocal;

    //If there are no nodes left, no nodes will be placed
    if (nodesLocal > 0) {

      //Adjust gapFactor to get a whole number given the number of nodes to place
      let gUpdate = (this.radialDistance * PI) / (nodesLocal - 1)  -  2 * this.graph.nodeRadius;

      //Adding to list of gaps - taking the high number to avoid numerical errors
      this.graph.gapList.push(Math.min(10**9, gUpdate));

      //Updating angle of increment (keeping PIs for reference)
      this.angleIncrement = PI * (2 * this.graph.nodeRadius + gUpdate) / (this.radialDistance * PI) ;

      //starting angle (270*)
      this.angle = PI * 3/2;

      //Looping through the number of nodes
      for (let i = 0; i < nodesLocal; i++) {
        this.graph.nodeCounter += 1
        this.addNode(this.graph.nodeCounter);
        this.angle -= this.angleIncrement; //moving counter clockwise

      }
    }
  }

  //Drawing all nodes in row
  drawNodes() {
    for (let i = 0; i < this.nodes.length; i++) {
      this.nodes[i].draw();
    }
  }

  //Adding a node to the row
  addNode(number) {

    //calculate new angle to (relative to parent)
    let newAngle = this.angle;

    //New point
    let newX = this.graph.rootNode.x + this.radialDistance * Math.sin(newAngle);
    let newY = this.graph.rootNode.y + this.radialDistance * Math.cos(newAngle);

    //Create new node
    let newNode = new Node(this.graph, newX, newY, number);

    //Id of current row
    newNode.row = number;

    //Adding the angle between center node and current node
    newNode.angle = newAngle;

    //Adding to list of nodes
    this.nodes.push(newNode);

    //Inserting into PQ
    this.graph.sortedNodes.insertMin(newNode, leftRight(newNode.angle) + distance(newNode, this.graph.rootNode) * HORIZ_WEIGHT);

  }

}


class Node {

  constructor(graph, x, y, id) {

    //ID of row
    this.row = null;

    //Local ID in row
    this.id = id;

    //Electoral chart
    this.graph = graph;

    //Dummy color
    this.color = "blue";

    //Coordinates
    this.x = x;
    this.y = y;

  }

  //Draw node
  draw() {
    drawNode(this.graph.ctx, this, this.graph.nodeRadius, this.color);
  }
}
