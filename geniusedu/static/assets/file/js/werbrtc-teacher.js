
    
    
    function store_live_stream()
    {
        show_id = '{{live_course.id}}';
        stream_id = $("#streamName").val()
        csrf_token = "{{csrf_token()}}";
        $.ajax({
            url:'/dashboard/store-live-records',
            method:'POST',
            data:{show_id:show_id,stream_id:stream_id,csrf_token:csrf_token},
            success:function(response){
                //console.log(response)
            }
        })
    }

    var token = "null";
    var start_publish_button = document.getElementById("start_publish_button");
    var stop_publish_button = document.getElementById("stop_publish_button");
    
    var streamNameBox = document.getElementById("streamName"); 
    //var streamNameBox = streamname
    var streamId;
    function getUrlParameter(sParam) {
        var sPageURL = decodeURIComponent(window.location.search.substring(1)),
            sURLVariables = sPageURL.split('&'),
            sParameterName,
            i;

        for (i = 0; i < sURLVariables.length; i++) {
            sParameterName = sURLVariables[i].split('=');

            if (sParameterName[0] === sParam) {
                return sParameterName[1] === undefined ? true : sParameterName[1];
            }
        }
    };
    
    var name = getUrlParameter("name");
    if(name !== "undefined")
    {
        streamNameBox.value = name;
    }
    

    function startPublishing() {
        
        streamId = streamNameBox.value;
        webRTCAdaptor.publish(streamId, token);
        //store_live_stream();
        broad_message();
       
    }

    function stopPublishing() {
        sid="{{live_course.id}}"; 
        var csrf_token = "{{csrf_token()}}"
        $.confirm({
                title: 'Confirm!',
                content: 'You want to finish the live class.',
                buttons: {
                    endclass: function () {
                        $.ajax({
                            url:'/dashboard/complete-live-show',
                            method:'POST',
                            data:{sid:sid,csrf_token:csrf_token},
                            beforeSend:function(){

                            },
                            success:function(response){
                                if (response.error==0){    
                                    webRTCAdaptor.stop(streamId);
                                    $("#stop_publish_button").hide()
                                    $("#start_publish_button").show();
                                    leave_room();
                                    window.location.href="{{url_for('dashboard')}}";  
                                }
                            }
                        })
                    },
                    close: function () {
                        
                    },
                    refresh:function(){
                        window.location.reload();
                    },

                }
            });
    }
    
    function enableDesktopCapture(enable) {
        if (enable == true) {
            webRTCAdaptor.switchDesktopCapture(streamId);
        }
        else {
            webRTCAdaptor.switchVideoCapture(streamId);
        }
    }
    
    function startAnimation() {

        $("#broadcastingInfo").fadeIn(800, function () {
          $("#broadcastingInfo").fadeOut(800, function () {
            var state = webRTCAdaptor.signallingState(streamId);
            if (state != null && state != "closed") {
                var iceState = webRTCAdaptor.iceConnectionState(streamId);
                if (iceState != null && iceState != "failed" && iceState != "disconnected") {
                    startAnimation();
                }
            }
          });
        });

      }

    var pc_config = null;

    var sdpConstraints = {
        OfferToReceiveAudio : false,
        OfferToReceiveVideo : false

    };
    
    var mediaConstraints = {
        video : true,
        audio : true
    };
    
    var path = 'livelearn.xyz:5443/WebRTCAppEE/websocket';
    
    var websocketURL =  "ws://" + path;
    
    if (location.protocol.startsWith("https")) {
        websocketURL = "wss://" + path;
    }
    
    
    var webRTCAdaptor = new WebRTCAdaptor({
        websocket_url : websocketURL,
        mediaConstraints : mediaConstraints,
        peerconnection_config : pc_config,
        sdp_constraints : sdpConstraints,
        //localVideoId : "localVideo",
        localVideoId : "video",
        debug:true,
        callback : function(info, description) {
            if (info == "initialized") {
                //console.log("initialized");
                start_publish_button.disabled = false;
                stop_publish_button.disabled = true;
            } else if (info == "publish_started") {
                //stream is being published
                //console.log("publish started");
                start_publish_button.disabled = true;
                stop_publish_button.disabled = false;
                startAnimation();
            } else if (info == "publish_finished") {
                //stream is being finished
                //console.log("publish finished");
                start_publish_button.disabled = false;
                stop_publish_button.disabled = true;
            }
            else if (info == "screen_share_extension_available") {
                 screen_share_checkbox.disabled = false;
                //console.log("screen share extension available");
                install_extension_link.style.display = "block";
            }
            else if (info == "screen_share_stopped") {
                //console.log("screen share stopped");
            }
            else if (info == "closed") {
                //console.log("Connection closed");
                if (typeof description != "undefined") {
                    //console.log("Connecton closed: " + JSON.stringify(description));
                }
            }
            else if (info == "pong") {
                //ping/pong message are sent to and received from server to make the connection alive all the time
                //It's especially useful when load balancer or firewalls close the websocket connection due to inactivity
            }
        },
        callbackError : function(error, message) {
            //some of the possible errors, NotFoundError, SecurityError,PermissionDeniedError
            
            console.log("error callback: " +  JSON.stringify(error));
            var errorMessage = JSON.stringify(error);
            if (typeof message != "undefined") {
                errorMessage = message;
            }
            var errorMessage = JSON.stringify(error);
            if (error.indexOf("NotFoundError") != -1) {
                errorMessage = "Camera or Mic are not found or not allowed in your device.";
            }
            else if (error.indexOf("NotReadableError") != -1 || error.indexOf("TrackStartError") != -1) {
                errorMessage = "Camera or Mic is being used by some other process that does not not allow these devices to be read.";
            }
            else if(error.indexOf("OverconstrainedError") != -1 || error.indexOf("ConstraintNotSatisfiedError") != -1) {
                errorMessage = "There is no device found that fits your video and audio constraints. You may change video and audio constraints."
            }
            else if (error.indexOf("NotAllowedError") != -1 || error.indexOf("PermissionDeniedError") != -1) {
                errorMessage = "You are not allowed to access camera and mic.";
            }
            else if (error.indexOf("TypeError") != -1) {
                errorMessage = "Video/Audio is required.";
            }
            else if (error.indexOf("UnsecureContext") != -1) {
                errorMessage = "Fatal Error: Browser cannot access camera and mic because of unsecure context. Please install SSL and access via https";
            }
            else if (error.indexOf("WebSocketNotSupported") != -1) {
                errorMessage = "Fatal Error: WebSocket not supported in this browser";
            }
        
            //alert(errorMessage);
        }
    });


