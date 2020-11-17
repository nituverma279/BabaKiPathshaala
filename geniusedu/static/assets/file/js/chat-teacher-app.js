$('#chat-content').scrollTop($('#chat-content')[0].scrollHeight);

        $(document).ready(function(){
            var show_id='';
            var sender_id='';
            var sid ='';
            $(document).on('click',".block_btn",function(){
                show_id=$(this).data('show_id');
                sender_id=$(this).data('sender_id');
                sid=$(this).data('sid');
                $(".user-block-modal").modal();    
            });

            $(document).on('click','.ban-btn',function(){
                block_chat_member(show_id,sender_id)  
                ban_user_from_room(sid); 
                $(".user-block-modal").modal('hide');    
            });
        });

        function block_chat_member(show_id,sender_id,ban_for){
            var broadcaster_id="{{current_user.id}}";
            var csrf_token = "{{csrf_token()}}"
            $.ajax({
                url:'/dashboard/block-chat-member',
                method:'POST',
                data:{show_id:show_id,sender_id:sender_id,broadcaster_id:broadcaster_id,csrf_token:csrf_token},
                beforeSend:function(){
                },
                success:function(response){
                    show_toast_message(response.message);
                    $(".user-block-modal").modal('hide');
                }
            })
        }



    chatWindow = document.getElementById('chat-content');
    var xH = chatWindow.scrollHeight;
    var namespace='/test';
    var socket = io.connect('https://' + document.domain + ':' +location.port+namespace);
    var room="{{live_course.class_title}}-{{live_course.id}}";
    // socket.emit('join', {room: room});
    stu_name="{{current_user.first_name}}";
    socket.emit('join', {room: room,student_name:stu_name});
    var csrf_token="{{csrf_token()}}"; 
   socket.on('connect', function() {

        var form= $('.message_input').keyup(function (e)
        {
            if (e.which == 13)
            {
                
                var sender_id,receiver_id,show_id,chat_msg,user_id
                sender_id=$(this).data('sender_id')
                receiver_id=$(this).data('receiver_id')
                show_id=$(this).data('show_id')
                user_id =$(this).data('user_id')
                chat_msg = $('.message_input').val()
                chat_msg.trim();
                if (chat_msg.length>0)
                {
                   
                    socket.emit('my_room_event', {room: room, show_id:show_id,user_id:user_id, sender_id:sender_id,receiver_id:receiver_id,chat_msg: chat_msg}); 
                    $.ajax({
                        url:"/dashboard/send-chat-msg",
                        method:'POST',
                        data:{user_id:user_id,sender_id:sender_id,receiver_id:receiver_id,chat_msg,show_id:show_id,csrf_token:csrf_token},
                        success:function(response){    
                        }    
                    });
                }
                $('.message_input').val('');
                chatWindow.scrollTo(0, xH);
            } 
        });
        
        var send_chat_msg= $('.message_input_btn').click(function (e)
        { 
            //socket.emit('my_event', {data:'Hi this is test message form the chat app.'}); 
            var sender_id,receiver_id,show_id,chat_msg,user_id
            sender_id=$(this).data('sender_id')
            receiver_id=$(this).data('receiver_id')
            show_id=$(this).data('show_id')
            user_id =$(this).data('user_id')
            chat_msg = $('.message_input').val()
            chat_msg.trim();
            if (chat_msg.length>0)
            {
                socket.emit('my_room_event', {room: room, show_id:show_id,user_id:user_id, sender_id:sender_id,receiver_id:receiver_id,chat_msg: chat_msg}); 
                $.ajax({
                    url:"/dashboard/send-chat-msg",
                    method:'POST',
                    data:{user_id:user_id,sender_id:sender_id,receiver_id:receiver_id,chat_msg,show_id:show_id,csrf_token:csrf_token},
                    success:function(response){    
                    }    
                });
            }

            $('.message_input').val('');
            chatWindow.scrollTo(0, xH);   
        });

    });


       socket.on('my_response', function(msg) {
         
         //console.log(msg);
         var chat_message_temp;
        if(msg['sender_id'] == msg['receiver_id'])
        {
             
            chat_message_temp=
                    '<div class="media media-chat">'+ 
                        '<div class="media-body">'+
                            '<p><b>@'+msg['user_id']+': </b>'+msg['chat_msg']+'</p>'+
                        '</div>'+
                    '</div>';
            $('div.message_holder').append(chat_message_temp);
        }
        else
        {
            var menu_icon="{{url_for('static',filename='assets/icons/menu.svg')}}";
            chat_message_temp=
                    '<div class="media media-chat media-chat-reverse">'+
                        '<div class="media-body">'+
                            '<p><button type="button" data-sid="'+msg['sid']+'" class="block_btn" data-show_id="'+msg['show_id']+'" data-sender_id="'+msg['sender_id']+'">'+
                                    '<img width="15" src="'+menu_icon+'">'+
                            '</button>  @'+msg['user_id']+':'+ msg['chat_msg']+'</p>'+
                        '</div>'+
                    '</div>';
            $('div.message_holder').append(chat_message_temp);
        } 
        if(msg) {
            $('#chat-content').scrollTop($('#chat-content')[0].scrollHeight);
        }
      });

       socket.on('my_response2',function(msg){

            var info ='<div class="d-flex pl-2 pr-2 pt-2">'+
                             '<div>'+
                                '<div class="bg-dark rounded-circle p-1">'+
                                    '<img width="25px" src="/static/assets/images/student.svg">'+
                                '</div>'+
                            '</div>'+
                             '<div class="p-2 pl-3">'+msg.chat_msg+'</div>'+
                         '</div>';
            $('#live-student-list').append(info);
        })

    function leave_room() {
        socket.emit('left', {'msg':'Hey all, Teacher has ended the show.','room':room}, function() {
                socket.disconnect();
        });      
    }

    function ban_user_from_room(id){
         
        socket.emit('ban',{'status':'banned','sid':id})
    }
    

    function broad_message(){
        socket.emit('broadmsg',{'message':'Hello all, I am now streaming live, please reload your page if you can not see the feed.','room':room})
    }




    $(document).ready(function(){
  $("#show_stud").click(function(){
    $("#hide_stud").show();
    $("#live-student-list").show();
    $("#show_stud").hide();
    $("#chat-content").hide();
    
  });
  $("#hide_stud").click(function(){
    $("#hide_stud").hide();
    $("#live-student-list").hide();
    $("#show_stud").show();
    $("#chat-content").show();
  });
});