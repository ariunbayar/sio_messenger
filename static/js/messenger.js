(function(){

    let formData = $("#form");
    let msgInput = $('#chatmessage');
    let chatHolder = $("#chat-messages");
    let socket = null;

    let threadItems = document.querySelectorAll('.messenger > .thread-list > ul.thread-list > li');

    function activateThreadItem(threadItems, threadItem) {
        threadItems.forEach((item) => item.classList.remove('active'));
        threadItem.classList.add('active');
    }

    threadItems.forEach((threadItem) => {

        threadItem.addEventListener('click', (e) => {
            activateThreadItem(threadItems, threadItem);
            let thread_id = threadItem.getAttribute('data-thread-id');
            let thread_url = threadItem.getAttribute('data-thread-history');
            closeCurrentSocket();
            initThread(thread_id);

            // var div = document.querySelectorAll('#message');
            chatHolder.html('')

            $.ajax({
                url: thread_url,
                dataType: 'json',
                success: function (data) {
                    if (data.thread_messages) {
                        data.thread_messages.forEach( function(message){
                            chatHolder.append('<div class="message" id="message">' +
                            '    <div class="time">' + message['date'] + '</div>' +
                            '    <div class="user">' + message['user'] + ':</div>' +
                            '    <div class="message">'+ message['message'] +'</div>' +
                            '</div>')
                            chatHolder.stop().animate({ scrollTop: chatHolder.prop('scrollHeight') })
                        });

                    }
                }
            })
        });

    });

    function getEndpointFor(thread_id) {
        let loc = window.location;
        let wsStart = loc.protocol == 'https' ? 'wss://' : 'ws://';
        return wsStart + loc.host + '/' + thread_id + '/';
    }

    function closeCurrentSocket() {
        if (socket === null) return;
        socket.close();
        socket = null;
    }

    function initThread(thread_id){

        let endpoint = getEndpointFor(thread_id);
        socket = new ReconnectingWebSocket(endpoint);

        socket.onmessage = function(e){
            var chatDataMsg = JSON.parse(e.data);
            chatHolder.append('<div class="message">' +
            '    <div class="time">12:00</div>' +
            '    <div class="user">' + chatDataMsg.username + ':</div>' +
            '    <div class="message">'+ chatDataMsg.message +'</div>' +
            '</div>');
            chatHolder.stop().animate({ scrollTop: chatHolder.prop('scrollHeight') });
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

})();
