
/*
 * Camera Buttons
 */
var testing;
var CameraButtons = function(blueprint3d) {

    var orbitControls = blueprint3d.three.controls;
    var three = blueprint3d.three;

    var panSpeed = 30;
    var directions = {
        UP: 1,
        DOWN: 2,
        LEFT: 3,
        RIGHT: 4
    }

    function init() {
        // Camera controls
        $("#zoom-in").click(zoomIn);
        $("#zoom-out").click(zoomOut);
        $("#zoom-in").dblclick(preventDefault);
        $("#zoom-out").dblclick(preventDefault);

        $("#reset-view").click(three.centerCamera)

        $("#move-left").click(function(){
            pan(directions.LEFT)
        })
        $("#move-right").click(function(){
            pan(directions.RIGHT)
        })
        $("#move-up").click(function(){
            pan(directions.UP)
        })
        $("#move-down").click(function(){
            pan(directions.DOWN)
        })

        $("#move-left").dblclick(preventDefault);
        $("#move-right").dblclick(preventDefault);
        $("#move-up").dblclick(preventDefault);
        $("#move-down").dblclick(preventDefault);

        //Play Controls
        $("#play").click(playAction);
        $("#pause").click(pauseAction);
    }

    function preventDefault(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    function pan(direction) {
        switch (direction) {
            case directions.UP:
                orbitControls.panXY(0, panSpeed);
                break;
            case directions.DOWN:
                orbitControls.panXY(0, -panSpeed);
                break;
            case directions.LEFT:
                orbitControls.panXY(panSpeed, 0);
                break;
            case directions.RIGHT:
                orbitControls.panXY(-panSpeed, 0);
                break;
        }
    }

    function zoomIn(e) {
        e.preventDefault();
        orbitControls.dollyIn(1.1);
        orbitControls.update();
    }

    function zoomOut(e) {
        e.preventDefault;
        orbitControls.dollyOut(1.1);
        orbitControls.update();
    }

    function playAction(){
        blueprint3d.model.play = true;
    }

    function pauseAction(){
        blueprint3d.model.play = false;
    }

    init();
}

/*
 * Context menu for selected item
 */

var ContextMenu = function(blueprint3d) {

    var scope = this;
    var selectedItem;
    var three = blueprint3d.three;

    function init() {
        $("#context-menu-delete").click(function(event) {
            selectedItem.remove();
        });

        three.itemSelectedCallbacks.add(itemSelected);
        three.itemUnselectedCallbacks.add(itemUnselected);

        initResize();

        $("#fixed").click(function() {
            var checked = $(this).prop('checked');
            selectedItem.setFixed(checked);
        });
    }

    function cmToIn(cm) {
        return cm / 2.54;
    }

    function inToCm(inches) {
        return inches * 2.54;
    }

    function itemSelected(item) {
        selectedItem = item;
        console.log("ITEM: ", item);
        $("#context-menu-name").text(item.metadata.itemName);

        $("#item-width").val(cmToIn(selectedItem.getWidth()).toFixed(0));
        $("#item-height").val(cmToIn(selectedItem.getHeight()).toFixed(0));
        $("#item-depth").val(cmToIn(selectedItem.getDepth()).toFixed(0));

        $("#context-menu").show();

        $("#fixed").prop('checked', item.fixed);
    }

    function resize() {
        selectedItem.resize(
            inToCm($("#item-height").val()),
            inToCm($("#item-width").val()),
            inToCm($("#item-depth").val())
        );
    }

    function initResize() {
        $("#item-height").change(resize);
        $("#item-width").change(resize);
        $("#item-depth").change(resize);
    }

    function itemUnselected() {
        selectedItem = null;
        $("#context-menu").hide();
    }

    init();
}

/*
 * Loading modal for items
 */

var ModalEffects = function(blueprint3d) {

    var scope = this;
    var blueprint3d = blueprint3d;
    var itemsLoading = 0;

    this.setActiveItem = function(active) {
        itemSelected = active;
        update();
    }

    function update() {
        if (itemsLoading > 0) {
            $("#loading-modal").show();
        } else {
            $("#loading-modal").hide();
        }
    }

    function init() {
        blueprint3d.model.scene.itemLoadingCallbacks.add(function() {
            itemsLoading += 1;
            update();
        });

        blueprint3d.model.scene.itemLoadedCallbacks.add(function() {
            itemsLoading -= 1;
            update();
        });

        update();
    }

    init();
}

/*
 * Side menu
 */

var SideMenu = function(blueprint3d, floorplanControls, modalEffects) {
    var blueprint3d = blueprint3d;
    var floorplanControls = floorplanControls;
    var modalEffects = modalEffects;

    var ACTIVE_CLASS = "active";

    var tabs = {
        "FLOORPLAN" : $("#floorplan_tab"),
        "SHOP" : $("#items_tab"),
        "DESIGN" : $("#design_tab")
    }

    var scope = this;
    this.stateChangeCallbacks = $.Callbacks();

    this.states = {
        "DEFAULT" : {
            "div" : $("#viewer"),
            "tab" : tabs.DESIGN
        },
        "FLOORPLAN" : {
            "div" : $("#floorplanner"),
            "tab" : tabs.FLOORPLAN
        },
        "SHOP" : {
            "div" : $("#add-items"),
            "tab" : tabs.SHOP
        }
    }

    // sidebar state
    var currentState = scope.states.FLOORPLAN;

    function init() {
        for (var tab in tabs) {
            var elem = tabs[tab];
            elem.click(tabClicked(elem));
        }

        $("#update-floorplan").click(floorplanUpdate);

        initLeftMenu();

        blueprint3d.three.updateWindowSize();
        handleWindowResize();

        initItems();

        setCurrentState(scope.states.DEFAULT);
    }

    function floorplanUpdate() {
        setCurrentState(scope.states.DEFAULT);
    }

    function tabClicked(tab) {
        return function() {
            // Stop three from spinning
            blueprint3d.three.stopSpin();

            // Selected a new tab
            for (var key in scope.states) {
                var state = scope.states[key];
                if (state.tab == tab) {
                    setCurrentState(state);
                    break;
                }
            }
        }
    }

    function setCurrentState(newState) {

        if (currentState == newState) {
            return;
        }

        // show the right tab as active
        if (currentState.tab !== newState.tab) {
            if (currentState.tab != null) {
                currentState.tab.removeClass(ACTIVE_CLASS);
            }
            if (newState.tab != null) {
                newState.tab.addClass(ACTIVE_CLASS);
            }
        }

        // set item unselected
        blueprint3d.three.getController().setSelectedObject(null);

        // show and hide the right divs
        currentState.div.hide()
        newState.div.show()

        // custom actions
        if (newState == scope.states.FLOORPLAN) {
            floorplanControls.updateFloorplanView();
            floorplanControls.handleWindowResize();
        }

        if (currentState == scope.states.FLOORPLAN) {
            blueprint3d.model.floorplan.update();
        }

        if (newState == scope.states.DEFAULT) {
            blueprint3d.three.updateWindowSize();
        }

        // set new state
        handleWindowResize();
        currentState = newState;

        scope.stateChangeCallbacks.fire(newState);
    }

    function initLeftMenu() {
        $( window ).resize( handleWindowResize );
        handleWindowResize();
    }

    function handleWindowResize() {
        $(".sidebar").height(window.innerHeight);
        $("#add-items").height(window.innerHeight);

    };

    // TODO: this doesn't really belong here
    function initItems() {
        $("#add-items").find(".add-item").mousedown(function(e) {
            var modelUrl = $(this).attr("model-url");
            var itemType = parseInt($(this).attr("model-type"));
            var metadata = {
                itemName: $(this).attr("model-name"),
                resizable: true,
                modelUrl: modelUrl,
                itemType: itemType
            }

            blueprint3d.model.scene.addItem(itemType, modelUrl, metadata);
            setCurrentState(scope.states.DEFAULT);
        });
    }

    init();

}

/*
 * Change floor and wall textures
 */

var TextureSelector = function (blueprint3d, sideMenu) {

    var scope = this;
    var three = blueprint3d.three;
    var isAdmin = isAdmin;

    var currentTarget = null;

    function initTextureSelectors() {
        $(".texture-select-thumbnail").click(function(e) {
            var textureUrl = $(this).attr("texture-url");
            var textureStretch = ($(this).attr("texture-stretch") == "true");
            var textureScale = parseInt($(this).attr("texture-scale"));
            currentTarget.setTexture(textureUrl, textureStretch, textureScale);

            e.preventDefault();
        });
    }

    function init() {
        three.wallClicked.add(wallClicked);
        three.floorClicked.add(floorClicked);
        three.itemSelectedCallbacks.add(reset);
        three.nothingClicked.add(reset);
        sideMenu.stateChangeCallbacks.add(reset);
        initTextureSelectors();
    }

    function wallClicked(halfEdge) {
        currentTarget = halfEdge;
        $("#floorTexturesDiv").hide();
        $("#wallTextures").show();
    }

    function floorClicked(room) {
        currentTarget = room;
        $("#wallTextures").hide();
        $("#floorTexturesDiv").show();
    }

    function reset() {
        $("#wallTextures").hide();
        $("#floorTexturesDiv").hide();
    }

    init();
}

/*
 * Floorplanner controls
 */

var ViewerFloorplanner = function(blueprint3d) {

    var canvasWrapper = '#floorplanner';

    // buttons
    var move = '#move';
    var remove = '#delete';
    var draw = '#draw';

    var activeStlye = 'btn-primary disabled';

    this.floorplanner = blueprint3d.floorplanner;

    var scope = this;

    function init() {

        $( window ).resize( scope.handleWindowResize );
        scope.handleWindowResize();

        // mode buttons
        scope.floorplanner.modeResetCallbacks.add(function(mode) {
            $(draw).removeClass(activeStlye);
            $(remove).removeClass(activeStlye);
            $(move).removeClass(activeStlye);
            if (mode == BP3D.Floorplanner.floorplannerModes.MOVE) {
                $(move).addClass(activeStlye);
            } else if (mode == BP3D.Floorplanner.floorplannerModes.DRAW) {
                $(draw).addClass(activeStlye);
            } else if (mode == BP3D.Floorplanner.floorplannerModes.DELETE) {
                $(remove).addClass(activeStlye);
            }

            if (mode == BP3D.Floorplanner.floorplannerModes.DRAW) {
                $("#draw-walls-hint").show();
                scope.handleWindowResize();
            } else {
                $("#draw-walls-hint").hide();
            }
        });

        $(move).click(function(){
            scope.floorplanner.setMode(BP3D.Floorplanner.floorplannerModes.MOVE);
        });

        $(draw).click(function(){
            scope.floorplanner.setMode(BP3D.Floorplanner.floorplannerModes.DRAW);
        });

        $(remove).click(function(){
            scope.floorplanner.setMode(BP3D.Floorplanner.floorplannerModes.DELETE);
        });
    }

    this.updateFloorplanView = function() {
        scope.floorplanner.reset();
    }

    this.handleWindowResize = function() {
        $(canvasWrapper).height(window.innerHeight - $(canvasWrapper).offset().top);
        scope.floorplanner.resizeView();
    };

    init();
};

var mainControls = function(blueprint3d) {
    var blueprint3d = blueprint3d;

    function newDesign() {
        blueprint3d.model.loadSerialized('{"floorplan":{"corners":{"f90da5e3-9e0e-eba7-173d-eb0b071e838e":{"x":204.85099999999989,"y":289.052},"da026c08-d76a-a944-8e7b-096b752da9ed":{"x":672.2109999999999,"y":289.052},"4e3d65cb-54c0-0681-28bf-bddcc7bdb571":{"x":672.2109999999999,"y":-178.308},"71d4f128-ae80-3d58-9bd2-711c6ce6cdf2":{"x":204.85099999999989,"y":-178.308}},"walls":[{"corner1":"71d4f128-ae80-3d58-9bd2-711c6ce6cdf2","corner2":"f90da5e3-9e0e-eba7-173d-eb0b071e838e","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0}},{"corner1":"f90da5e3-9e0e-eba7-173d-eb0b071e838e","corner2":"da026c08-d76a-a944-8e7b-096b752da9ed","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0}},{"corner1":"da026c08-d76a-a944-8e7b-096b752da9ed","corner2":"4e3d65cb-54c0-0681-28bf-bddcc7bdb571","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0}},{"corner1":"4e3d65cb-54c0-0681-28bf-bddcc7bdb571","corner2":"71d4f128-ae80-3d58-9bd2-711c6ce6cdf2","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0}}],"wallTextures":[],"floorTextures":{},"newFloorTextures":{}},"items":[]}');
    }

    function loadDesign() {
        files = $("#loadFile").get(0).files;
        var reader  = new FileReader();
        reader.onload = function(event) {
            var data = event.target.result;
            blueprint3d.model.loadSerialized(data);
        }
        reader.readAsText(files[0]);
    }

    function saveDesign() {
        var data = blueprint3d.model.exportSerialized();
        var a = window.document.createElement('a');
        var blob = new Blob([data], {type : 'text'});
        a.href = window.URL.createObjectURL(blob);
        a.download = 'design.blueprint3d';
        document.body.appendChild(a)
        a.click();
        document.body.removeChild(a)
    }

    function init() {
        $("#new").click(newDesign);
        $("#loadFile").change(loadDesign);
        $("#saveFile").click(saveDesign);
    }

    init();
}

/*
 * Initialize!
 */

$(document).ready(function() {

    // main setup
    var opts = {
        floorplannerElement: 'floorplanner-canvas',
        threeElement: '#viewer',
        threeCanvasElement: 'three-canvas',
        textureDir: "models/textures/",
        widget: false
    }
    var blueprint3d = new BP3D.Blueprint3d(opts);

    var modalEffects = new ModalEffects(blueprint3d);
    var viewerFloorplanner = new ViewerFloorplanner(blueprint3d);
    var contextMenu = new ContextMenu(blueprint3d);
    var sideMenu = new SideMenu(blueprint3d, viewerFloorplanner, modalEffects);
    var textureSelector = new TextureSelector(blueprint3d, sideMenu);
    var cameraButtons = new CameraButtons(blueprint3d);
    mainControls(blueprint3d);

    $.ajax('/js/LabGSI.blueprint3d', {
        async: false,
        dataType: 'text',
        success: function (data) {
            testing = data;
        }
    });
    //var json ='{"floorplan":{"corners":{"56d9ebd1-91b2-875c-799d-54b3785fca1f":{"x":630.555,"y":-227.58400000000006},"8f4a050d-e102-3c3f-5af9-3d9133555d76":{"x":294.64,"y":-227.58400000000006},"4e312eca-6c4f-30d1-3d9a-a19a9d1ee359":{"x":294.64,"y":232.664},"254656bf-8a53-3987-c810-66b349f49b19":{"x":745.7439999999998,"y":232.664},"11d25193-4411-fbbf-78cb-ae7c0283164b":{"x":1044.7019999999998,"y":232.664},"edf0de13-df9f-cd6a-7d11-9bd13c36ce12":{"x":1044.7019999999998,"y":-105.66399999999999},"e7db8654-efe1-bda2-099a-70585874d8c0":{"x":745.7439999999998,"y":-105.66399999999999}},"walls":[{"corner1":"4e312eca-6c4f-30d1-3d9a-a19a9d1ee359","corner2":"254656bf-8a53-3987-c810-66b349f49b19","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"https://blueprint-dev.s3.amazonaws.com/uploads/floor_wall_texture/file/wallmap_yellow.png","stretch":true,"scale":null}},{"corner1":"254656bf-8a53-3987-c810-66b349f49b19","corner2":"e7db8654-efe1-bda2-099a-70585874d8c0","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"https://blueprint-dev.s3.amazonaws.com/uploads/floor_wall_texture/file/wallmap_yellow.png","stretch":true,"scale":null}},{"corner1":"56d9ebd1-91b2-875c-799d-54b3785fca1f","corner2":"8f4a050d-e102-3c3f-5af9-3d9133555d76","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"https://blueprint-dev.s3.amazonaws.com/uploads/floor_wall_texture/file/wallmap_yellow.png","stretch":true,"scale":null}},{"corner1":"8f4a050d-e102-3c3f-5af9-3d9133555d76","corner2":"4e312eca-6c4f-30d1-3d9a-a19a9d1ee359","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"https://blueprint-dev.s3.amazonaws.com/uploads/floor_wall_texture/file/wallmap_yellow.png","stretch":true,"scale":null}},{"corner1":"254656bf-8a53-3987-c810-66b349f49b19","corner2":"11d25193-4411-fbbf-78cb-ae7c0283164b","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0}},{"corner1":"11d25193-4411-fbbf-78cb-ae7c0283164b","corner2":"edf0de13-df9f-cd6a-7d11-9bd13c36ce12","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"https://blueprint-dev.s3.amazonaws.com/uploads/floor_wall_texture/file/light_brick.jpg","stretch":false,"scale":100}},{"corner1":"edf0de13-df9f-cd6a-7d11-9bd13c36ce12","corner2":"e7db8654-efe1-bda2-099a-70585874d8c0","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0}},{"corner1":"e7db8654-efe1-bda2-099a-70585874d8c0","corner2":"56d9ebd1-91b2-875c-799d-54b3785fca1f","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"https://blueprint-dev.s3.amazonaws.com/uploads/floor_wall_texture/file/wallmap_yellow.png","stretch":true,"scale":null}}],"wallTextures":[],"floorTextures":{},"newFloorTextures":{"11d25193-4411-fbbf-78cb-ae7c0283164b,254656bf-8a53-3987-c810-66b349f49b19,e7db8654-efe1-bda2-099a-70585874d8c0,edf0de13-df9f-cd6a-7d11-9bd13c36ce12":{"url":"https://blueprint-dev.s3.amazonaws.com/uploads/floor_wall_texture/file/light_fine_wood.jpg","scale":300}}},"items":[{"item_name":"Full Bed","item_type":1,"model_url":"https://blueprint-dev.s3.amazonaws.com/uploads/item_model/model/39/ik_nordli_full.js","xpos":939.5525544513545,"ypos":50,"zpos":-15.988409993966997,"rotation":-1.5707963267948966,"scale_x":1,"scale_y":1,"scale_z":1,"fixed":false},{"item_name":"Bedside table - White","item_type":1,"model_url":"https://blueprint-dev.s3.amazonaws.com/uploads/item_model/model/353/cb-archnight-white_baked.js","xpos":1001.0862865204286,"ypos":31.15939942141,"zpos":86.4297300551338,"rotation":-0.7872847644705953,"scale_x":1,"scale_y":1,"scale_z":1,"fixed":false},{"item_name":"Open Door","item_type":7,"model_url":"https://blueprint-dev.s3.amazonaws.com/uploads/item_model/model/174/open_door.js","xpos":745.2440185546875,"ypos":110.5,"zpos":64.8291839065202,"rotation":-1.5707963267948966,"scale_x":1.7003089598352215,"scale_y":0.997292171703541,"scale_z":0.999415040540576,"fixed":false},{"item_name":"Window","item_type":3,"model_url":"https://blueprint-dev.s3.amazonaws.com/uploads/item_model/model/165/whitewindow.js","xpos":886.8841174461031,"ypos":139.1510114697785,"zpos":-105.16400146484375,"rotation":0,"scale_x":1,"scale_y":1,"scale_z":1,"fixed":false},{"item_name":"Dresser - White","item_type":1,"model_url":"https://blueprint-dev.s3.amazonaws.com/uploads/item_model/model/478/we-narrow6white_baked.js","xpos":898.0548281668393,"ypos":35.611997646165,"zpos":201.10860458067486,"rotation":-3.141592653589793,"scale_x":1,"scale_y":1,"scale_z":1,"fixed":false},{"item_name":"Window","item_type":3,"model_url":"https://blueprint-dev.s3.amazonaws.com/uploads/item_model/model/165/whitewindow.js","xpos":534.9620937975317,"ypos":137.60931398864443,"zpos":-227.08399963378906,"rotation":0,"scale_x":1,"scale_y":1,"scale_z":1,"fixed":false},{"item_name":"Window","item_type":3,"model_url":"https://blueprint-dev.s3.amazonaws.com/uploads/item_model/model/165/whitewindow.js","xpos":295.1400146484375,"ypos":141.43383044055196,"zpos":123.2280598724867,"rotation":1.5707963267948966,"scale_x":1,"scale_y":1,"scale_z":1,"fixed":false},{"item_name":"Media Console - White","item_type":1,"model_url":"https://blueprint-dev.s3.amazonaws.com/uploads/item_model/model/400/cb-clapboard_baked.js","xpos":658.6568227980731,"ypos":67.88999754395999,"zpos":-141.50237235990153,"rotation":-0.8154064090423808,"scale_x":1,"scale_y":1,"scale_z":1,"fixed":false},{"item_name":"Blue Rug","item_type":8,"model_url":"https://blueprint-dev.s3.amazonaws.com/uploads/item_model/model/440/cb-blue-block-60x96.js","xpos":905.8690190229256,"ypos":0.250005,"zpos":44.59927303228528,"rotation":-1.5707963267948966,"scale_x":1,"scale_y":1,"scale_z":1,"fixed":false},{"item_name":"NYC Poster","item_type":2,"model_url":"https://blueprint-dev.s3.amazonaws.com/uploads/item_model/model/77/nyc-poster2.js","xpos":1038.448276049687,"ypos":146.22618581237782,"zpos":148.65033715350484,"rotation":-1.5707963267948966,"scale_x":1,"scale_y":1,"scale_z":1,"fixed":false},{"item_name":"Sofa - Grey","item_type":1,"model_url":"https://blueprint-dev.s3.amazonaws.com/uploads/item_model/model/596/cb-rochelle-gray_baked.js","xpos":356.92671999154373,"ypos":42.54509923821,"zpos":-21.686174295784554,"rotation":1.5707963267948966,"scale_x":1,"scale_y":1,"scale_z":1,"fixed":false},{"item_name":"Coffee Table - Wood","item_type":1,"model_url":"https://blueprint-dev.s3.amazonaws.com/uploads/item_model/model/68/ik-stockholmcoffee-brown.js","xpos":468.479104587435,"ypos":24.01483158034958,"zpos":-23.468458996048412,"rotation":1.5707963267948966,"scale_x":1,"scale_y":1,"scale_z":1,"fixed":false},{"item_name":"Floor Lamp","item_type":1,"model_url":"https://blueprint-dev.s3.amazonaws.com/uploads/item_model/model/614/ore-3legged-white_baked.js","xpos":346.697102333121,"ypos":72.163997943445,"zpos":-175.19915302127583,"rotation":0,"scale_x":1,"scale_y":1,"scale_z":1,"fixed":false},{"item_name":"Red Chair","item_type":1,"model_url":"https://blueprint-dev.s3.amazonaws.com/uploads/item_model/model/723/ik-ekero-orange_baked.js","xpos":397.676038151142,"ypos":37.50235073007,"zpos":156.31701312594373,"rotation":2.4062972386507093,"scale_x":1,"scale_y":1,"scale_z":1,"fixed":false},{"item_name":"Window","item_type":3,"model_url":"https://blueprint-dev.s3.amazonaws.com/uploads/item_model/model/165/whitewindow.js","xpos":374.7738207971076,"ypos":138.62749831597068,"zpos":-227.08399963378906,"rotation":0,"scale_x":1,"scale_y":1,"scale_z":1,"fixed":false},{"item_name":"Closed Door","item_type":7,"model_url":"https://blueprint-dev.s3.amazonaws.com/uploads/item_model/model/617/closed-door28x80_baked.js","xpos":637.2176377788675,"ypos":110.80000022010701,"zpos":232.16400146484375,"rotation":3.141592653589793,"scale_x":1,"scale_y":1,"scale_z":1,"fixed":false},{"item_name":"Bookshelf","item_type":1,"model_url":"https://blueprint-dev.s3.amazonaws.com/uploads/item_model/model/388/cb-kendallbookcasewalnut_baked.js","xpos":533.1460416453955,"ypos":92.17650034119151,"zpos":207.7644213268835,"rotation":3.141592653589793,"scale_x":1,"scale_y":1,"scale_z":1,"fixed":false}]}'
    //var json = '{"floorplan":{"corners":{"f90da5e3-9e0e-eba7-173d-eb0b071e838e":{"x":204.85099999999989,"y":289.052},"da026c08-d76a-a944-8e7b-096b752da9ed":{"x":672.2109999999999,"y":289.052},"4e3d65cb-54c0-0681-28bf-bddcc7bdb571":{"x":672.2109999999999,"y":-178.308},"71d4f128-ae80-3d58-9bd2-711c6ce6cdf2":{"x":204.85099999999989,"y":-178.308},"a":{"x":0,"y":289.052},"b":{"x":0,"y":-178.308}},"walls":[{"corner1":"71d4f128-ae80-3d58-9bd2-711c6ce6cdf2","corner2":"f90da5e3-9e0e-eba7-173d-eb0b071e838e","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0}},{"corner1":"f90da5e3-9e0e-eba7-173d-eb0b071e838e","corner2":"da026c08-d76a-a944-8e7b-096b752da9ed","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0}},{"corner1":"da026c08-d76a-a944-8e7b-096b752da9ed","corner2":"4e3d65cb-54c0-0681-28bf-bddcc7bdb571","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0}},{"corner1":"4e3d65cb-54c0-0681-28bf-bddcc7bdb571","corner2":"71d4f128-ae80-3d58-9bd2-711c6ce6cdf2","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0}},{"corner1":"a","corner2":"f90da5e3-9e0e-eba7-173d-eb0b071e838e","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0}},{"corner1":"a","corner2":"b","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0}},{"corner1":"b","corner2":"71d4f128-ae80-3d58-9bd2-711c6ce6cdf2","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0}}],"wallTextures":[],"floorTextures":{},"newFloorTextures":{}},"items":[]}'
    var json = testing;
    //var prueba = '{"floorplan":{"corners":{"C92":{"x":0,"y":-200},"C120":{"x":200,"y":-200},"C186":{"x":400,"y":-200},"C142":{"x":600,"y":-200},"C39":{"x":800,"y":-200},"C189":{"x":1000,"y":-200},"C83":{"x":1200,"y":-200},"C28":{"x":1400,"y":-200},"C34":{"x":1600,"y":-200},"C130":{"x":1800,"y":-200},"C100":{"x":2000,"y":-200},"C73":{"x":0,"y":200},"C201":{"x":200,"y":200},"C67":{"x":400,"y":200},"C79":{"x":600,"y":200},"C15":{"x":800,"y":200},"C97":{"x":1000,"y":200},"C182":{"x":1200,"y":200},"C9":{"x":1400,"y":200},"C27":{"x":1600,"y":200},"C190":{"x":1800,"y":200},"C117":{"x":2000,"y":200},"C138":{"x":0,"y":400},"C124":{"x":400,"y":400},"C143":{"x":800,"y":400},"C163":{"x":1200,"y":400},"C116":{"x":1600,"y":400},"C30":{"x":2000,"y":400},"C42":{"x":0,"y":800},"C200":{"x":400,"y":800},"C194":{"x":800,"y":800},"C191":{"x":1200,"y":800},"C131":{"x":1600,"y":800},"C37":{"x":2000,"y":800},"C162":{"x":16.5,"y":14.425},"C38":{"x":-4.15,"y":7.375},"C203":{"x":10.285,"y":2.8200000000000003},"C102":{"x":8.5,"y":6.425},"C45":{"x":-4.15,"y":1.625},"C90":{"x":0.7149999999999999,"y":-0.8200000000000001},"C184":{"x":19.285,"y":5.335},"C22":{"x":-0.6550000000000002,"y":3.5},"C128":{"x":11.5,"y":9.165},"C185":{"x":19.285,"y":0.665},"C136":{"x":13.285,"y":-0.07500000000000018},"C146":{"x":16.285,"y":-0.07500000000000018},"C199":{"x":4.715,"y":-0.8200000000000001},"C153":{"x":14.5,"y":15.75},"C169":{"x":3.715,"y":-0.8200000000000001},"C105":{"x":10.5,"y":12.32},"C188":{"x":14.715,"y":0.17999999999999994},"C123":{"x":12.5,"y":14.32},"C70":{"x":4.5,"y":6.32},"C170":{"x":8.285,"y":-0.8200000000000001},"C54":{"x":1.5,"y":3.575},"C55":{"x":1.5,"y":-0.5750000000000002},"C173":{"x":16.5,"y":18.32},"C127":{"x":11.5,"y":13.835},"C41":{"x":0.5,"y":3.875},"C19":{"x":-4.155,"y":0.4049999999999998},"C63":{"x":2.5,"y":0.6799999999999999},"C95":{"x":8.5,"y":10.32},"C113":{"x":2.715,"y":-0.8200000000000001},"C16":{"x":0.5,"y":-2.095},"C17":{"x":11,"y":4.5},"C193":{"x":12.5,"y":14.575},"C177":{"x":21.155,"y":7.595000000000001},"C183":{"x":16.5,"y":13.905},"C145":{"x":11.715,"y":-0.07500000000000018},"C76":{"x":8.285,"y":6.82},"C161":{"x":16.5,"y":18.575},"C165":{"x":13.715,"y":-0.07500000000000018},"C74":{"x":5.5,"y":7.32},"C93":{"x":10.285,"y":6.82},"C46":{"x":6.41,"y":9.15},"C96":{"x":8.5,"y":6.68},"C137":{"x":16.285,"y":6.82},"C154":{"x":14.5,"y":13.25},"C118":{"x":10.5,"y":8.425},"C152":{"x":15.5,"y":14.25},"C62":{"x":2.5,"y":4.32},"C129":{"x":11.5,"y":13.575},"C10":{"x":-4.155,"y":-0.5950000000000002},"C13":{"x":6.655,"y":2.5},"C32":{"x":2.215,"y":4.5},"C109":{"x":13.285,"y":6.82},"C86":{"x":7.5,"y":9.32},"C174":{"x":16.5,"y":14.68},"C115":{"x":6.715,"y":-0.07500000000000018},"C75":{"x":5.5,"y":3.6799999999999997},"C192":{"x":14.285,"y":0.17999999999999994},"C81":{"x":6.5,"y":6},"C60":{"x":3.5,"y":5.32},"C36":{"x":1.5,"y":0.19999999999999996},"C48":{"x":2.5,"y":6.65},"C166":{"x":18.285,"y":-0.07500000000000018},"C53":{"x":2.5,"y":0.4249999999999998},"C125":{"x":12.5,"y":14.835},"C2":{"x":1.5,"y":4.1},"C103":{"x":12.285,"y":6.82},"C175":{"x":19.285,"y":5.3},"C56":{"x":-2.41,"y":-0.07500000000000018},"C43":{"x":4.15,"y":8.375},"C89":{"x":0.21499999999999986,"y":2.5},"C65":{"x":-0.7850000000000001,"y":1.5},"C91":{"x":5.285,"y":-0.8200000000000001},"C64":{"x":3.785,"y":1.5},"C0":{"x":-5.5,"y":-0.6000000000000001},"C110":{"x":8.715,"y":6.82},"C187":{"x":16.5,"y":14.165},"C150":{"x":15.5,"y":13.68},"C35":{"x":1.5,"y":2.8},"C160":{"x":14.5,"y":11.65},"C52":{"x":2.5,"y":4.575},"C155":{"x":12.715,"y":-0.8500000000000001},"C99":{"x":9.5,"y":11.32},"C25":{"x":8.91,"y":4.5},"C121":{"x":14.285,"y":6.82},"C80":{"x":6.5,"y":7},"C29":{"x":0.5,"y":4.65},"C122":{"x":9.715,"y":6.82},"C164":{"x":15.5,"y":13.425},"C6":{"x":1.5,"y":2.575},"C172":{"x":13.715,"y":6.82},"C135":{"x":8.715,"y":-0.07500000000000018},"C149":{"x":15.5,"y":17.32},"C104":{"x":7.715,"y":6.82},"C168":{"x":7.5,"y":7},"C84":{"x":9.285,"y":6.82},"C107":{"x":1.7149999999999999,"y":-0.8200000000000001},"C101":{"x":8.5,"y":10.575},"C151":{"x":15.5,"y":16.75},"C114":{"x":7.285,"y":-0.8200000000000001},"C144":{"x":13.5,"y":11.425},"C4":{"x":0.5,"y":3.1},"C98":{"x":6.715,"y":6.82},"C40":{"x":-0.6500000000000004,"y":3.5},"C11":{"x":4.155,"y":-0.5950000000000002},"C197":{"x":8.5,"y":9},"C57":{"x":6.41,"y":-0.07500000000000018},"C94":{"x":5.715,"y":6.82},"C139":{"x":14.5,"y":16.32},"C106":{"x":10.5,"y":8.68},"C141":{"x":14.5,"y":16.575},"C24":{"x":-3.41,"y":9.15},"C167":{"x":7.5,"y":8},"C85":{"x":4.715,"y":6.82},"C68":{"x":6.285,"y":6.82},"C148":{"x":12.715,"y":6.82},"C178":{"x":12.844999999999999,"y":7.595000000000001},"C21":{"x":7.655,"y":3.5},"C171":{"x":18.285,"y":6.82},"C126":{"x":12.5,"y":10.165},"C196":{"x":15.285,"y":-0.07500000000000018},"C198":{"x":8.5,"y":8},"C33":{"x":5.785,"y":3.5},"C66":{"x":2.5,"y":3},"C7":{"x":1.5,"y":0.42500000000000004},"C72":{"x":7.285,"y":6.82},"C156":{"x":17.285,"y":-0.8500000000000001},"C181":{"x":0.34499999999999975,"y":4.5},"C108":{"x":6.285,"y":-0.8200000000000001},"C51":{"x":-0.9100000000000001,"y":3.5},"C20":{"x":-4.155,"y":5.595000000000001},"C133":{"x":13.5,"y":15.32},"C179":{"x":21.155,"y":2.405},"C69":{"x":1.7149999999999999,"y":6.82}http://www.online-convert.com/file-format/ogv,"C195":{"x":10.715,"y":-0.07500000000000018},"C58":{"x":5.285,"y":6.82},"C1":{"x":7.5,"y":-0.6000000000000001},"C23":{"x":5.41,"y":9.15},"C132":{"x":10.715,"y":6.82},"C47":{"x":-2.41,"y":9.15},"C202":{"x":10.285,"y":-0.8200000000000001},"C78":{"x":6.5,"y":8.32},"C71":{"x":4.5,"y":2.6799999999999997},"C5":{"x":0.5,"y":-2.1},"C50":{"x":7.91,"y":3.5},"C180":{"x":8.655000000000001,"y":4.5},"C82":{"x":5.5,"y":6},"C88":{"x":4.785,"y":2.5},"C49":{"x":2.5,"y":-1.6500000000000004},"C44":{"x":-4.15,"y":8.375},"C31":{"x":6.785,"y":4.5},"C18":{"x":-2,"y":4.5},"C140":{"x":14.5,"y":12.68},"C3":{"x":1.5,"y":-1.1},"C8":{"x":0.5,"y":1.575},"C158":{"x":15.5,"y":12.65},"C157":{"x":15.5,"y":18.35},"C159":{"x":14.5,"y":17.35},"C12":{"x":-4.155,"y":4.595000000000001},"C112":{"x":11.5,"y":9.68},"C61":{"x":3.5,"y":1.68},"C26":{"x":0.08999999999999986,"y":4.5},"C87":{"x":7.5,"y":5.68},"C77":{"x":3.715,"y":6.82},"C59":{"x":0.7149999999999999,"y":6.82},"C176":{"x":19.285,"y":2.7},"C119":{"x":7.715,"y":-0.07500000000000018},"C14":{"x":-1.6550000000000002,"y":2.5},"C147":{"x":17.285,"y":6.82},"C111":{"x":11.5,"y":13.32},"C134":{"x":13.5,"y":11.68}},"walls":[{"corner1":"C92","corner2":"C120","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0}},{"corner1":"C120","corner2":"C186","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0}},{"corner1":"C186","corner2":"C142","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0}},{"corner1":"C142","corner2":"C39","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0}},{"corner1":"C39","corner2":"C189","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0}},{"corner1":"C189","corner2":"C83","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0}},{"corner1":"C83","corner2":"C28","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0}},{"corner1":"C28","corner2":"C34","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0}},{"corner1":"C34","corner2":"C130","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0}},{"corner1":"C130","corner2":"C100","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0}},{"corner1":"C100","corner2":"C117","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0}},{"corner1":"C117","corner2":"C190","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0}},{"corner1":"C190","corner2":"C27","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0}},{"corner1":"C27","corner2":"C9","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0}},{"corner1":"C9","corner2":"C182","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0}},{"corner1":"C182","corner2":"C97","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0}},{"corner1":"C97","corner2":"C15","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0}},{"corner1":"C15","corner2":"C79","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0}},{"corner1":"C79","corner2":"C67","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0}},{"corner1":"C67","corner2":"C201","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0}},{"corner1":"C201","corner2":"C73","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0}},{"corner1":"C73","corner2":"C92","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0}},{"corner1":"C120","corner2":"C201","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0}},{"corner1":"C186","corner2":"C67","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0}},{"corner1":"C142","corner2":"C79","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0}},{"corner1":"C39","corner2":"C15","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0}},{"corner1":"C189","corner2":"C97","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0}},{"corner1":"C83","corner2":"C182","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0}},{"corner1":"C28","corner2":"C9","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0}},{"corner1":"C34","corner2":"C27","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0}},{"corner1":"C130","corner2":"C190","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0}},{"corner1":"C73","corner2":"C138","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0}},{"corner1":"C138","corner2":"C124","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0}},{"corner1":"C124","corner2":"C143","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0}},{"corner1":"C143","corner2":"C163","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0}},{"corner1":"C163","corner2":"C116","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0}},{"corner1":"C116","corner2":"C30","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0}},{"corner1":"C30","corner2":"C117","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0}},{"corner1":"C30","corner2":"C37","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0}},{"corner1":"C37","corner2":"C131","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0}},{"corner1":"C131","corner2":"C191","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0}},{"corner1":"C191","corner2":"C194","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0}},{"corner1":"C194","corner2":"C200","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0}},{"corner1":"C200","corner2":"C42","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0}},{"corner1":"C42","corner2":"C138","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0}},{"corner1":"C124","corner2":"C200","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0}},{"corner1":"C143","corner2":"C194","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0}},{"corner1":"C163","corner2":"C191","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0}},{"corner1":"C116","corner2":"C131","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0}}],"wallTextures":[],"floorTextures":{},"newFloorTextures":{}},"items":[]}';
    // This serialization format needs work
    // Load a simple rectangle room
//  blueprint3d.model.loadSerialized('{"floorplan":{"corners":{"f90da5e3-9e0e-eba7-173d-eb0b071e838e":{"x":204.85099999999989,"y":289.052},"da026c08-d76a-a944-8e7b-096b752da9ed":{"x":672.2109999999999,"y":289.052},"4e3d65cb-54c0-0681-28bf-bddcc7bdb571":{"x":672.2109999999999,"y":-178.308},"71d4f128-ae80-3d58-9bd2-711c6ce6cdf2":{"x":204.85099999999989,"y":-178.308},"a":{"x":0,"y":289.052},"b":{"x":0,"y":-178.308}},"walls":[{"corner1":"71d4f128-ae80-3d58-9bd2-711c6ce6cdf2","corner2":"f90da5e3-9e0e-eba7-173d-eb0b071e838e","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0}},{"corner1":"f90da5e3-9e0e-eba7-173d-eb0b071e838e","corner2":"da026c08-d76a-a944-8e7b-096b752da9ed","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0}},{"corner1":"da026c08-d76a-a944-8e7b-096b752da9ed","corner2":"4e3d65cb-54c0-0681-28bf-bddcc7bdb571","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0}},{"corner1":"4e3d65cb-54c0-0681-28bf-bddcc7bdb571","corner2":"71d4f128-ae80-3d58-9bd2-711c6ce6cdf2","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0}},{"corner1":"a","corner2":"f90da5e3-9e0e-eba7-173d-eb0b071e838e","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0}},{"corner1":"a","corner2":"b","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0}},{"corner1":"b","corner2":"71d4f128-ae80-3d58-9bd2-711c6ce6cdf2","frontTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0},"backTexture":{"url":"rooms/textures/wallmap.png","stretch":true,"scale":0}}],"wallTextures":[],"floorTextures":{},"newFloorTextures":{}},"items":[]}');
//     blueprint3d.model.loadSerialized(blueprint3d.model.floorJSON);
    blueprint3d.model.loadSerialized(json);
});
