model = {
    position: [0, 0],
    obstacles: [],
    distances: {}
}

update_model = function() {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/api/get_obstacles', false);
    xhr.send();

    obstacles = JSON.parse(xhr.responseText);
    model.obstacles = obstacles;

    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/api/get_distances', false);
    xhr.send();

    distances = JSON.parse(xhr.responseText);
    model.distances = distances;
}

update_view = function() {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/api/get_grid_info', false);
    xhr.send();

    grid_info = JSON.parse(xhr.responseText);
    view.grid_info = grid_info;

    var img = new Image();
    img.onload = function() {
        view.grid = img;
        render();
    }
    img.src = '/api/get_grid/' + Math.random();

    update_info();
}

update = function() {
    update_model();
    update_view();
}

update();
setInterval(update, 2000);