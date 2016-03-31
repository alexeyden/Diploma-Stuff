view = {};
view.canvas = document.getElementById('canvas');
view.context = view.canvas.getContext('2d');
view.scale = 20.0;
view.width = 800;
view.height = 500;
view.origin = [view.width/2/view.scale, view.height/2/view.scale];
view.grid = null;
view.grid_info = null;

render_obstacles = function() {
    view.context.lineWidth = 1;
    view.context.strokeStyle = '#ff0000';

    for(var i = 0; i < model.obstacles.length; i++) {
        obstacle = model.obstacles[i];

        view.context.beginPath();

        for(var j = 0; j < obstacle.length; j++) {
            var p = obstacle[j];

            var x = (p[0] - model.position[0] + view.origin[0]) * view.scale;
            var y = (p[1] - model.position[1] + view.origin[1]) * view.scale;

            if(j == 0) {
                view.context.moveTo(x, y);
                continue;
            }

            view.context.lineTo(x, y);
            view.context.moveTo(x, y);
            view.context.stroke();
        }
    }

    view.context.lineWidth = 0;
    view.context.strokeStyle = '#909090';
    view.context.beginPath();

    var x0 = (model.position[0] + view.origin[0] - Math.floor(model.position[0] + view.origin[0])) * view.scale;
    var y0 = (model.position[1] + view.origin[1] - Math.floor(model.position[1] + view.origin[1])) * view.scale;

    for(var x = x0; x < view.width; x += view.scale) {
        view.context.moveTo(x, view.height);
        view.context.lineTo(x, view.height - 10);
    }
    for(var y = y0; y < view.height; y += view.scale) {
        view.context.moveTo(view.width, y);
        view.context.lineTo(view.width - 10, y);
    }
    view.context.stroke();
}

render = function() {
    view.context.clearRect(0, 0, view.canvas.width, view.canvas.height);

    var x = (view.grid_info.position[0] + view.origin[0]) * view.scale;
    var y = (view.grid_info.position[1] + view.origin[1]) * view.scale;

    view.context.drawImage(view.grid, x, y, view.grid_info.size * view.scale, view.grid_info.size * view.scale);

    render_obstacles();
}

wheel = function(e) {
    var e = window.event || e;
	var delta = Math.max(-1, Math.min(1, (e.wheelDelta || -e.detail)));

	view.scale += delta;
	view.origin = [view.width/2/view.scale, view.height/2/view.scale];
	render();
}

document.getElementById('canvas').addEventListener("mousewheel", wheel, false);
document.getElementById('canvas').addEventListener("DOMMouseScroll", wheel, false);