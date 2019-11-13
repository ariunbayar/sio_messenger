(function(){

    let ThreadList = (() => {

        function ThreadList(child_elements, fn_thread_selected) {

            this.active_child_element = null;

            this.child_elements = {};

            this.on_thread_selected = fn_thread_selected;

            document.querySelectorAll(child_elements).forEach((child_element) => {

                let thread_id = child_element.getAttribute('data-thread-id');
                this.child_elements[thread_id] = child_element;

                child_element.addEventListener('click', (e) => {
                    this.activate(thread_id);
                });

            });
        }

        ThreadList.prototype.activate = function (thread_id) {

            let child_element = this.child_elements[thread_id];

            if (this.active_child_element === child_element) {
                return;
            }

            if (this.active_child_element) {
                this.active_child_element.classList.remove('active');
            }
            child_element.classList.add('active');
            this.active_child_element = child_element;

            let thread_url = child_element.getAttribute('data-thread-history');

            this.on_thread_selected(thread_id, thread_url);
        };

        return ThreadList;

    })();

    let formData = $("#form");
    let msgInput = $('#chatmessage');
    let chatHolder = $("#chat-messages");
    let socket = null;

    let endpoint = getEndpointFor();
    socket = new ReconnectingWebSocket(endpoint);

    socket.onopen = function(e){
        console.log('open', e)
    }

    function getEndpointFor() {
        let loc = window.location;
        let wsStart = loc.protocol == 'https' ? 'wss://' : 'ws://';
        return wsStart + loc.host + '/';
    }

    // {
    //     action: 'thread_message'
    //     params: {
    //         thread_id: <thread_id>,
    //         message: <message>,
    //     }
    // }

    // formData.submit(function(event){
    //     event.preventDefault()
    //     var msgText = msgInput.val()
    //     var finalData = {
    //         'action': 'thread_message'
    //         'params': {
    //             'thread_id': ,
    //             'message': msgText,
    //         }
    //     }
    //
    //     socket.send(JSON.stringify(finalData))
    //     msgInput.val('')
    //     formData[0].reset()
    // })

    let thread_list = new ThreadList('.messenger > .thread-list > ul.thread-list > li', (thread_id, thread_url) => {

        initThread(thread_id);

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

        formData.submit(function(event){
            event.preventDefault()
            var msgText = msgInput.val()
            var data = {
                'action': 'thread_message',
                'params': {
                    'thread_id': thread_id,
                    'message': msgText,
                },
            }

            socket.send(JSON.stringify(data))
            msgInput.val('')
            formData[0].reset()
        })
    });

    function initThread(thread_id){

        console.log(thread_id);
        console.log(socket);
        chatHolder.html('');

        socket.onmessage = function(e){
            var chatDataMsg = JSON.parse(e.data);
            chatHolder.append('<div class="message">' +
            '    <div class="time">12:00</div>' +
            '    <div class="user">' + chatDataMsg.username + ':</div>' +
            '    <div class="message">'+ chatDataMsg.message +'</div>' +
            '</div>');
            chatHolder.stop().animate({ scrollTop: chatHolder.prop('scrollHeight') });
        }
        socket.onerror = function(e){
            console.log("error", e)
        }
        socket.onclose = function(e){
            console.log("close", e)
        }
    }

})();
