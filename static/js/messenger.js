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

    let thread_list = new ThreadList('.messenger > .thread-list > ul.thread-list > li', (thread_id, thread_url) => {
        closeCurrentSocket();
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

        chatHolder.html('');

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
