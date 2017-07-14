/// <reference path="../../lib/jQuery.d.ts" />
/// <reference path="../../lib/three.d.ts" />

/// <reference path="controller.ts" />
/// <reference path="floorPlan.ts" />
/// <reference path="lights.ts" />
/// <reference path="skybox.ts" />
/// <reference path="controls.ts" />
/// <reference path="hud.ts" />
/// <reference path="human.ts" />

module BP3D.Three {
    export var Main = function (model, element, canvasElement, opts) {
        var scope = this;

        var options = {
            resize: true,
            pushHref: false,
            spin: true,
            spinSpeed: .00002,
            clickPan: true,
            canMoveFixedItems: false
        }

        // override with manually set options
        for (var opt in options) {
            if (options.hasOwnProperty(opt) && opts.hasOwnProperty(opt)) {
                options[opt] = opts[opt]
            }
        }

        var scene = model.scene;

        var model = model;
        this.element = $(element);
        var domElement;

        var camera;
        var renderer;
        this.controls;
        var canvas;
        var controller;
        var floorplan;

        var meshes = [];
        var mixers = [];
        var human = new Human(scene, model);

        var video;
        var imageContext;
        var textureVideo;
        var paused = 1;
        var timeRender = 0;
        var stepTime = 1000;
        // var step = 1;

        //var canvas;
        //var canvasElement = canvasElement;

        var needsUpdate = false;

        var lastRender = Date.now();
        var mouseOver = false;
        var hasClicked = false;

        var hud;

        this.heightMargin;
        this.widthMargin;
        this.elementHeight;
        this.elementWidth;

        this.itemSelectedCallbacks = $.Callbacks(); // item
        this.itemUnselectedCallbacks = $.Callbacks();

        this.wallClicked = $.Callbacks(); // wall
        this.floorClicked = $.Callbacks(); // floor
        this.nothingClicked = $.Callbacks();
        // var customUniforms;

        function init() {
            THREE.ImageUtils.crossOrigin = "";

            domElement = scope.element.get(0) // Container
            camera = new THREE.PerspectiveCamera(45, 1, 1, 14500);
            renderer = new THREE.WebGLRenderer({
                antialias: true,
                preserveDrawingBuffer: true // required to support .toDataURL()
            });
            renderer.autoClear = false,
                renderer.shadowMapEnabled = true;
            renderer.shadowMapSoft = true;
            renderer.shadowMapType = THREE.PCFSoftShadowMap;
            renderer.setClearColor( 0x808080, 1);
            var skybox = new Three.Skybox(scene);

            scope.controls = new Three.Controls(camera, domElement);

            hud = new Three.HUD(scope);

            controller = new Three.Controller(
                scope, model, camera, scope.element, scope.controls, hud);

            domElement.appendChild(renderer.domElement);

            // handle window resizing
            scope.updateWindowSize();
            if (options.resize) {
                $(window).resize(scope.updateWindowSize);
            }

            // setup camera nicely
            scope.centerCamera();
            model.floorplan.fireOnUpdatedRooms(scope.centerCamera);
            var lights = new Three.Lights(scene, model.floorplan);

            floorplan = new Three.Floorplan(scene,
                model.floorplan, scope.controls);
            animate();

            scope.element.mouseenter(function () {
                mouseOver = false;
            }).mouseleave(function () {
                mouseOver = false;
            }).click(function () {
                hasClicked = false;
            });

            // var plane = new THREE.PlaneGeometry( 102.106, 102.106, 4, 4 );
            //
            // var lavaTexture = THREE.ImageUtils.loadTexture( 'lava.jpg' );
            // var lavaMaterial = new THREE.MeshBasicMaterial( { map: lavaTexture } );
            // var mesh = new THREE.Mesh( plane, lavaMaterial );
            // mesh.rotation.x = -Math.PI / 2;
            // mesh.position.y = 50;
            // scene.add( mesh );

            // var cubeGeometry = new THREE.CubeGeometry( 102.106, 102.106, 102.106 );

            // var materialArray = [];
            // materialArray.push(new THREE.MeshBasicMaterial( { map: THREE.ImageUtils.loadTexture( 'lava.jpg' ) }));
            // materialArray.push(new THREE.MeshBasicMaterial( { map: THREE.ImageUtils.loadTexture( 'lava.jpg' ) }));
            // materialArray.push(new THREE.MeshBasicMaterial( { map: THREE.ImageUtils.loadTexture( 'lava.jpg' ) }));
            // materialArray.push(new THREE.MeshBasicMaterial( { map: THREE.ImageUtils.loadTexture( 'lava.jpg' ) }));
            // materialArray.push(new THREE.MeshBasicMaterial( { map: THREE.ImageUtils.loadTexture( 'lava.jpg' ) }));
            // materialArray.push(new THREE.MeshBasicMaterial( { map: THREE.ImageUtils.loadTexture( 'lava.jpg' ) }));
            // var cubeMaterial = new THREE.MeshFaceMaterial(materialArray);


            // var crateTexture =  THREE.ImageUtils.loadTexture( 'lava.jpg' );
            // var crateMaterial = new THREE.MeshBasicMaterial( { map: crateTexture } );
            //
            // var DiceBlueGeom = new THREE.CubeGeometry( 102.106, 102.106, 102.106, 1, 1, 1 );
            // var DiceBlue = new THREE.Mesh( DiceBlueGeom, crateMaterial );
            // DiceBlue.position.y = 102.106/2;
            // // DiceBlue.position.set(60, 50, -100);
            // scene.add( DiceBlue );



            // var lavaTexture =  THREE.ImageUtils.loadTexture( 'lava.jpg');
            // lavaTexture.wrapS = lavaTexture.wrapT = THREE.RepeatWrapping;
            // // multiplier for distortion speed
            // var baseSpeed = 0.02;
            // // number of times to repeat texture in each direction
            // var repeatS = 4.0;
            // var repeatT = 4.0;
            // // texture used to generate "randomness", distort all other textures
            // var noiseTexture =  THREE.ImageUtils.loadTexture( 'cloud.png' );
            // noiseTexture.wrapS = noiseTexture.wrapT = THREE.RepeatWrapping;
            // // magnitude of noise effect
            // var noiseScale = 0.5;
            //
            // // texture to additively blend with base image texture
            // var blendTexture =  THREE.ImageUtils.loadTexture( 'lava.jpg' );
            // blendTexture.wrapS = blendTexture.wrapT = THREE.RepeatWrapping;
            // // multiplier for distortion speed
            // var blendSpeed = 0.01;
            // // adjust lightness/darkness of blended texture
            // var blendOffset = 0.25;
            //
            // // texture to determine normal displacement
            // var bumpTexture = noiseTexture;
            // bumpTexture.wrapS = bumpTexture.wrapT = THREE.RepeatWrapping;
            // // multiplier for distortion speed
            // var bumpSpeed   = 0.15;
            // // magnitude of normal displacement
            // var bumpScale   = 40.0;
            //
            // // use "this." to create global object
            //  customUniforms = {
            //     baseTexture: 	{ type: "t", value: lavaTexture },
            //     baseSpeed:		{ type: "f", value: baseSpeed },
            //     repeatS:		{ type: "f", value: repeatS },
            //     repeatT:		{ type: "f", value: repeatT },
            //     noiseTexture:	{ type: "t", value: noiseTexture },
            //     noiseScale:		{ type: "f", value: noiseScale },
            //     blendTexture:	{ type: "t", value: blendTexture },
            //     blendSpeed: 	{ type: "f", value: blendSpeed },
            //     blendOffset: 	{ type: "f", value: blendOffset },
            //     bumpTexture:	{ type: "t", value: bumpTexture },
            //     bumpSpeed: 		{ type: "f", value: bumpSpeed },
            //     bumpScale: 		{ type: "f", value: bumpScale },
            //     alpha: 			{ type: "f", value: 1.0 },
            //     time: 			{ type: "f", value: 1.0 }
            // };
            //
            // // create custom material from the shader code above
            // //   that is within specially labeled script tags
            // var customMaterial = new THREE.ShaderMaterial(
            //     {
            //         uniforms: customUniforms,
            //         vertexShader:   document.getElementById( 'vertexShader'   ).textContent,
            //         fragmentShader: document.getElementById( 'fragmentShader' ).textContent
            //     }   );
            //
            // // var DiceBlueGeom = new THREE.CubeGeometry( 102.106, 102.106, 102.106, 1, 1, 1 );
            // var ballGeometry = new THREE.SphereGeometry( 60, 64, 64 );
            // var ball = new THREE.Mesh(	ballGeometry, customMaterial );
            // var ball2 = new THREE.Mesh(	ballGeometry, customMaterial );
            // ball.position.set(0, 51, 0);
            // ball2.position.set(102.106, 51, 0);
            // scene.add( ball );
            // scene.add( ball2 );

        }

        function spin() {
            if (options.spin && !mouseOver && !hasClicked) {
                // var theta = 2 * Math.PI * options.spinSpeed * (Date.now() - lastRender);
                // scope.controls.rotateLeft(theta);
                scope.controls.update()
            }
        }

        this.dataUrl = function () {
            var dataUrl = renderer.domElement.toDataURL("image/png");
            return dataUrl;
        }

        this.stopSpin = function () {
            hasClicked = true;
        }

        this.options = function () {
            return options;
        }

        this.getModel = function () {
            return model;
        }

        this.getScene = function () {
            return scene;
        }

        this.getController = function () {
            return controller;
        }

        this.getCamera = function () {
            return camera;
        }

        this.needsUpdate = function () {
            needsUpdate = true;

        }
        function shouldRender() {
            // Do we need to draw a new frame
            if (scope.controls.needsUpdate || controller.needsUpdate || needsUpdate || model.scene.needsUpdate) {
                scope.controls.needsUpdate = false;
                controller.needsUpdate = false;
                needsUpdate = false;
                model.scene.needsUpdate = false;
                return true;
            } else {
                return false;
            }
        }

        function render() {
            spin();
            if (shouldRender()) {
                renderer.clear();
                renderer.render(scene.getScene(), camera);
                renderer.clearDepth();
                renderer.render(hud.getScene(), camera);
            }


            //Check if the simulation is paused
            if(model.play) {

                human.moveAll(scene.step);

                lastRender = Date.now();
                if( lastRender - scene.initialTime >= stepTime){
                    scene.initialTime = lastRender;
                    scene.step += 1;
                    scene.flag = 1;
                }

                if (scene.video &&  scene.video.readyState === scene.video.HAVE_ENOUGH_DATA ) {

                    scene.imageContext.drawImage( scene.video, 0, 0 );

                    if ( scene.textureVideo ) scene.textureVideo.needsUpdate = true;

                }
            }
            else{

                if(paused ==1) {
                    paused+=1;

                }
            }
            var date = new Date();
            scene.fps = 1000/( date.getTime() - timeRender);
            timeRender = date.getTime();
        };



        function animate() {
            var delay = 50;
            var delta = 0.04;
            if(scene.customUniforms!=undefined){
                scene.customUniforms.time.value += delta;

            }
            setTimeout(function () {
                requestAnimationFrame(animate);
            }, delay);
            render();

        }

        this.rotatePressed = function () {
            controller.rotatePressed();
        }

        this.rotateReleased = function () {
            controller.rotateReleased();
        }

        this.setCursorStyle = function (cursorStyle) {
            domElement.style.cursor = cursorStyle;
        };

        this.updateWindowSize = function () {
            scope.heightMargin = scope.element.offset().top;
            scope.widthMargin = scope.element.offset().left;

            scope.elementWidth = scope.element.innerWidth();
            if (options.resize) {
                scope.elementHeight = window.innerHeight - scope.heightMargin;
            } else {
                scope.elementHeight = scope.element.innerHeight();
            }

            camera.aspect = scope.elementWidth / scope.elementHeight;
            camera.updateProjectionMatrix();

            renderer.setSize(scope.elementWidth, scope.elementHeight);
            needsUpdate = true;
        }

        this.centerCamera = function () {
            var yOffset = 150.0;

            var pan = model.floorplan.getCenter();
            pan.y = yOffset;

            scope.controls.target = pan;

            var distance = model.floorplan.getSize().z * 1.5;

            var offset = pan.clone().add(
                new THREE.Vector3(0, distance, distance));
            //scope.controls.setOffset(offset);
            camera.position.copy(offset);

            scope.controls.update();
        }

        // projects the object's center point into x,y screen coords
        // x,y are relative to top left corner of viewer
        this.projectVector = function (vec3, ignoreMargin) {
            ignoreMargin = ignoreMargin || false;

            var widthHalf = scope.elementWidth / 2;
            var heightHalf = scope.elementHeight / 2;

            var vector = new THREE.Vector3();
            vector.copy(vec3);
            vector.project(camera);

            var vec2 = new THREE.Vector2();

            vec2.x = (vector.x * widthHalf) + widthHalf;
            vec2.y = - (vector.y * heightHalf) + heightHalf;

            if (!ignoreMargin) {
                vec2.x += scope.widthMargin;
                vec2.y += scope.heightMargin;
            }

            return vec2;
        }

        init();
    }
}
