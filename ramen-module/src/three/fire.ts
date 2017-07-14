/// <reference path="../../lib/jQuery.d.ts" />
/// <reference path="../../lib/three.d.ts" />

module BP3D.Three {
    export var Fire = function (scene, model) {


        var customMaterial;
        var ballGeometry;

        function init(){


            var lavaTexture =  THREE.ImageUtils.loadTexture( 'lava.jpg');
            lavaTexture.wrapS = lavaTexture.wrapT = THREE.RepeatWrapping;
            // multiplier for distortion speed
            var baseSpeed = 0.02;
            // number of times to repeat texture in each direction
            var repeatS = 4.0;
            var repeatT = 4.0;
            // texture used to generate "randomness", distort all other textures
            var noiseTexture =  THREE.ImageUtils.loadTexture( 'cloud.png' );
            noiseTexture.wrapS = noiseTexture.wrapT = THREE.RepeatWrapping;
            // magnitude of noise effect
            var noiseScale = 0.5;

            // texture to additively blend with base image texture
            var blendTexture =  THREE.ImageUtils.loadTexture( 'lava.jpg' );
            blendTexture.wrapS = blendTexture.wrapT = THREE.RepeatWrapping;
            // multiplier for distortion speed
            var blendSpeed = 0.01;
            // adjust lightness/darkness of blended texture
            var blendOffset = 0.25;

            // texture to determine normal displacement
            var bumpTexture = noiseTexture;
            bumpTexture.wrapS = bumpTexture.wrapT = THREE.RepeatWrapping;
            // multiplier for distortion speed
            var bumpSpeed   = 0.15;
            // magnitude of normal displacement
            var bumpScale   = 40.0;

            // use "this." to create global object
            scene.customUniforms = {
                baseTexture: 	{ type: "t", value: lavaTexture },
                baseSpeed:		{ type: "f", value: baseSpeed },
                repeatS:		{ type: "f", value: repeatS },
                repeatT:		{ type: "f", value: repeatT },
                noiseTexture:	{ type: "t", value: noiseTexture },
                noiseScale:		{ type: "f", value: noiseScale },
                blendTexture:	{ type: "t", value: blendTexture },
                blendSpeed: 	{ type: "f", value: blendSpeed },
                blendOffset: 	{ type: "f", value: blendOffset },
                bumpTexture:	{ type: "t", value: bumpTexture },
                bumpSpeed: 		{ type: "f", value: bumpSpeed },
                bumpScale: 		{ type: "f", value: bumpScale },
                alpha: 			{ type: "f", value: 1.0 },
                time: 			{ type: "f", value: 1.0 }
            };

            // create custom material from the shader code above
            //   that is within specially labeled script tags
            customMaterial = new THREE.ShaderMaterial(
                {
                    uniforms: scene.customUniforms,
                    vertexShader:   document.getElementById( 'vertexShader'   ).textContent,
                    fragmentShader: document.getElementById( 'fragmentShader' ).textContent
                }   );

            // var DiceBlueGeom = new THREE.CubeGeometry( 102.106, 102.106, 102.106, 1, 1, 1 );
            ballGeometry = new THREE.SphereGeometry( 60, 64, 64 );
            // var ball = new THREE.Mesh(	ballGeometry, customMaterial );
            // var ball2 = new THREE.Mesh(	ballGeometry, customMaterial );
            // ball.position.set(-200, 51, 0);
            // ball2.position.set(102.106, 51, 0);
            // scene.add( ball );
            // scene.add( ball2 );


        }

        this.setFire = function(position){
            var mesh = new THREE.Mesh(	ballGeometry, customMaterial );
            mesh.position.x = position.x;
            mesh.position.y = 51;
            mesh.position.z = position.y;
            scene.add(mesh);
        }



        init();
    }
}



