/// <reference path="../../lib/three.d.ts" />

module BP3D.Three {
    export var LoadMovement = function (scene, model) {

        var scene = scene;
        var model = model;

        var movementJSON;
        var humans = [];
        function init(){
            $.ajax('/js/movement.json', {
                async: false,
                dataType: 'text',
                success: function (data2) {
                    movementJSON = data2;
                }
            });

            var jsonMove = JSON.parse(movementJSON);
            humans = jsonMove.humans;
            // for (var i = 0; i<humans.length; i++){
            //
            //     positions.push(humans[i].positions);
            // }


            // var human = new Human(scene, model, humans);
        }

        init();
    }
}