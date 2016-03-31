$ = function(id) {
    return document.getElementById(id);
}

update_info = function() {
    if(model.distances.left !== undefined)
        $('range_left').innerHTML = model.distances.left.toFixed(3);

    if(model.distances.right !== undefined)
        $('range_right').innerHTML = model.distances.right.toFixed(3);

    if(model.distances.front !== undefined)
        $('range_front').innerHTML = model.distances.front.toFixed(3);

    if(model.distances.rear !== undefined)
        $('range_rear').innerHTML = model.distances.rear.toFixed(3);
}