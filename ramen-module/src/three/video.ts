/// <reference path="../../lib/jQuery.d.ts" />
/// <reference path="../../lib/three.d.ts" />

module BP3D.Three {
    export var Video = function (scene, model, room) {

        var plane;
        var materialVideo;
        var mesh;

        function init(){
            scene.video = document.getElementById( 'video' );
            var image = document.createElement( 'canvas' );
            // image.width = 480;
            // image.height = 204;
            image.width = 426;
            image.height = 240;

            scene.imageContext = image.getContext( '2d' );
            scene.imageContext.fillStyle = '#000000';
            scene.imageContext.fillRect( 0, 0, 512, 240 );
            // scene.imageContext.fillRect( 0, 0, 512, 256 );426

            scene.textureVideo = new THREE.Texture( image );

            materialVideo = new THREE.MeshBasicMaterial( { map: scene.textureVideo, overdraw: 0.5 } );
            // plane = new THREE.PlaneGeometry( 480/6.5, 204/6.5, 4, 4 );

            plane = new THREE.PlaneGeometry( 426/6.5, 240/6.5, 4, 4 );



            getTV();

        }

        function getTV(){
            var items = scene.getItems();
            for (var i=0; i<items.length; i++){
                if( items[i].metadata.itemName == "Media Console - White"){
                    if(room == items[i].getRoom(model)){
                        mesh = new THREE.Mesh( plane, materialVideo );
                        mesh.scale.x = mesh.scale.y = mesh.scale.z = 1.7;
                        scene.add(mesh);
                        setPosition(mesh,items[i]);
                    }


                }
            }
        }

        function setPosition(mesh, item){
            var orientation = item.getOrientation();
            mesh.rotation.y = item.rotation.y;
            switch (orientation){
                case "NORTH":
                    mesh.position.x = item.position.x;
                    mesh.position.y = 104;
                    mesh.position.z = item.position.z - 2;
                    break;
                case "WEST":
                    mesh.position.x = item.position.x - 2;
                    mesh.position.y = 104;
                    mesh.position.z = item.position.z;
                    break;
                case "SOUTH":
                    mesh.position.x = item.position.x;
                    mesh.position.y = 104;
                    mesh.position.z = item.position.z + 2;
                    break;
                case "EAST":
                    mesh.position.x = item.position.x + 2;
                    mesh.position.y = 104;
                    mesh.position.z = item.position.z;
                    break;
            }
        }

        function offTV() {
            scene.remove(mesh);
        }


        init();
    }
}
