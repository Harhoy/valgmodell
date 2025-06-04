

class PQSeats {

    constructor() {
        self.units = {}
    }

    addElement(key, value) {
        self.units[key] = value;
    }

    getMax() {
    
        let maxVal = -1;
        let maxId = null;
        
        for (const [key, value] of Object.entries(self.units)) {
            if (value > maxVal) {
                maxVal = value;
                maxId = key;
            }
        }
    delete self.units[maxId]
    return maxId;
    }

    getLength() {
        return Object.keys(self.units).length;
    }
}


function largest_remainder(seats, targetSum) {

    // sum total seats
    let sumSeats = 0;
    for (let i = 0; i < seats.length; i++) {
        sumSeats += seats[i];
    }

    //calculate fair entitlement
    let fair_entitlement = seats.map((x) => x / sumSeats * targetSum);

    //round down
    let whole_seats = fair_entitlement.map((x) => Math.floor(x));

    //Total "seats" allocated
    const totalSeats = whole_seats.reduce((sum, x) => sum + x);
    
    // pq of remainders
    const pq = new PQSeats();

    for (let i = 0; i < seats.length; i++){
        pq.addElement(i, fair_entitlement[i] - whole_seats[i]);
    }
    
    //get leftover seats
    let leftOverSeats = targetSum - totalSeats;

    while (leftOverSeats > 0 && pq.getLength() > 0) {
        whole_seats[pq.getMax()] += 1;
        leftOverSeats -= 1;
    }

    return whole_seats;
}

/*
window.addEventListener('load', () => {

    seats = [50.12, 40.56, 67, 19.23, 15.4, 10.4, 9.5];

    console.log(largest_remainder(seats, 169));

})
*/
