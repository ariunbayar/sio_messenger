function InitThread(thread_id){
	var loc = window.location
	var formData = $("#form")
	var msgInput = $('#chatmessage')
	var chatHolder = $("#chat-messages")
	var me = $("#myUsername").val()

	var wsStart = 'ws://'
	if (loc.protocol == 'https'){
	    wsStart = 'wss://'
	}

	var endpoint = wsStart + loc.host + '/' + thread_id + '/'
	console.log(endpoint)
	var socket = new ReconnectingWebSocket(endpoint)

	socket.onmessage = function(e){
	    var chatDataMsg = JSON.parse(e.data)
	    chatHolder.append('<div class="message">' +
        '    <div class="time">12:00</div>' +
        '    <div class="user">' + chatDataMsg.username + ':</div>' +
        '    <div class="message">'+ chatDataMsg.message +'</div>' +
        '</div>')
	}
	socket.onopen = function(e){
	    formData.submit(function(event){
	        event.preventDefault()
	        var msgText = msgInput.val()
	        var finalData = {
	            'message': msgText
	        }

	        socket.send(JSON.stringify(finalData))
	        msgInput.val('')
	        formData[0].reset()
	    })
	}
	socket.onerror = function(e){
	    console.log("error", e)
	}
	socket.onclose = function(e){
	    console.log("close", e)
	}	
}