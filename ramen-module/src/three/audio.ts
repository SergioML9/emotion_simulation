/// <reference path="../../lib/jQuery.d.ts" />
/// <reference path="../../lib/three.d.ts" />

module BP3D.Three {
    export var Audio = function (camera, scene) {
        var listener;
        function init(){
            //Create an AudioListener and add it to the camera
            listener = new THREE.AudioListener();
            camera.add(listener);
            backgroundMusic();
        }

        function backgroundMusic(){
            // create a global audio source
            var sound = new THREE.Audio(listener);

            var audioLoader = new THREE.AudioLoader();

            //Load a sound and set it as the Audio object's buffer
            audioLoader.load('358232_j_s_song.ogg', function (buffer) {
                sound.setBuffer(buffer);
                sound.setLoop(true);
                sound.setVolume(0.5);
                sound.play();
            }, function (){
            }, function (){
            });
        }

        function directionalMusic(){
            //Create the PositionalAudio object (passing in the listener)
            var sound = new THREE.PositionalAudio( listener );

            //Load a sound and set it as the PositionalAudio object's buffer
            var audioLoader = new THREE.AudioLoader();
            audioLoader.load( '358232_j_s_song.ogg', function( buffer ) {
                sound.setBuffer( buffer );
                sound.setRefDistance( 20 );
                sound.play();
            }, function() {
            }, function() {
            });

            //Create an object for the sound to play from
            var sphere = new THREE.SphereGeometry( 20, 32, 16 );
            var material = new THREE.MeshPhongMaterial( { color: 0xff2200 } );
            var mesh = new THREE.Mesh( sphere, material );
            scene.add( mesh );
            //Finally add the sound to the mesh
            mesh.add( sound );
        }
        init();
    }
}
