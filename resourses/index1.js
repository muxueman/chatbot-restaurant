$( document ).ready(function(){
  var apigClient = apigClientFactory.newClient();

  $( '.time_sent' ).html(new Date().toLocaleString());
  $( '.write_msg' ).keypress(function(e){
    if(e.which == 13) {
        // enter pressed
        $( '.send_btn' ).click()
    }
  });


  var params = {
    // This is where any modeled request parameters should be added.
    // The key is the parameter name, as it is defined in the API in API Gateway.
    // param0: '',
    // param1: ''
  };

  $( '.send_btn' ).on('click', function(){
    var msg = $( ".write_msg" ).val(); 
    if(msg!=''){
      $( '.msg_record' ).append(
          '<div class="outgoing_msg"><div class="sent_msg"><p>' 
          + msg + '</p><span class="time_sent">' 
          + new Date().toLocaleString() 
          + '</span> </div></div>'
      ); 
      $( ".write_msg" ).val('')

      // var body = {
      //     "description": ""
      // };
      var body = {
                "messages": [
                    {
                        "type": "string",
                        "unstructured": {
                        "id": "0",
                        "text": msg,
                        "timestamp": "12/20/2018"
                        }
                    }
                ]
            };

      apigClient.chatbotPost(params, body).then(function(result){
        // Add success callback code here.  
        console.log(result)

        $( '.msg_record' ).append(
            '<div class="incoming_msg"> \
                <div class="bot_pic"> <img src="profile1.jpg" alt="bot" height="50" width="50"> </div> \
                <div class="bot_side"> \
                    <div class="bot_msg"> \
                        <p>' + result["data"]["body"] + '</p> \
                        <span class="time_sent">' + new Date().toLocaleString() + '</span> \
                    </div> \
                </div> \
            </div>'
          );
        $('.msg_record').scrollTop($('.msg_record')[0].scrollHeight);

        // console.log(typeof(result["data"]["fullfilled"]))
        // if(result["data"]["fullfilled"]==true){

        // }
                        

      }).catch( function(result){
        // Add error callback code here.
        console.log("error happens somewhere");
        console.log(result);
      });

      // apigClient.chatbotPost(params, body).then(function(result){
      //   // Add success callback code here.  
      //   console.log(result)
      //   // console.log(typeof(result["data"]["fullfilled"]))
      //   // if(result["data"]["fullfilled"]==true){
          
      //   // }
                        
      // }).catch( function(result){
      //   // Add error callback code here.
      //   console.log("error happens somewhere");
      //   console.log(result);
      // });
      

    }
  });

  // $('.msg_record').scrollTop($('.msg_record')[0].scrollHeight);


  // var params = {
  //   // This is where any modeled request parameters should be added.
  //   // The key is the parameter name, as it is defined in the API in API Gateway.
  //   param0: '',
  //   param1: ''
  // };

  // var body = {
  //   // This is where you define the body of the request,
  // };

  // var additionalParams = {
  //   // If there are any unmodeled query parameters or headers that must be
  //   //   sent with the request, add them here.
  //   headers: {
  //     param0: '',
  //     param1: ''
  //   },
  //   queryParams: {
  //     param0: '',
  //     param1: ''
  //   }
  // };

  


});