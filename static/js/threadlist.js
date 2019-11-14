(function(Utils){

    let ThreadList = (() => {

        function ThreadList(child_elements, fn_thread_selected) {

            this.active_child_element = null;

            this.child_elements = {};

            this.on_thread_selected = fn_thread_selected;

            document.querySelectorAll(child_elements).forEach((child_element) => {

                let thread_id = parseInt(child_element.getAttribute('data-thread-id'));
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

    let ChatBox = (() => {

        function ChatBox(config) {

            let message_form = document.querySelector(config.message_form_selector);
            let message_field = message_form.querySelector(config.message_field_selector);
            let message_list = document.querySelector(config.message_list_selector);

            message_form.addEventListener('submit', (event) => {
                event.preventDefault();
                this.sendMessage(message_field.value);
                event.target.reset();
            });

            this.thread_id = null;
            this.on_send_message = config.on_send_message;
            this.message_list = message_list;

        }

        ChatBox.prototype.sendMessage = function sendMessage(message) {

            if (this.thread_id === null) {
                return;
            }

            this.on_send_message(this.thread_id, message);

        }

        ChatBox.prototype.setThread = function setThread(thread_id) {

            this.thread_id = thread_id;

        }

        ChatBox.prototype.clearMessageList = function clearMessageList() {
            while (this.message_list.firstChild) {
                this.message_list.removeChild(this.message_list.firstChild);
            }
        }

        ChatBox.prototype.addMessages = function addMessages(messages) {

            let newDomNode = (tag, cls, innerText) => {
                let el = document.createElement(tag);
                el.classList.add(cls);
                if (innerText) {
                    let innerTextEscaped = Utils.escapeHtml(innerText);
                    let elText = document.createTextNode(innerTextEscaped);
                    el.appendChild(elText);
                }
                return el;
            }

            messages.forEach((message) => {
                let time = new Date(message.timestamp * 1000);
                let time_repr = ("0" + time.getHours()).slice(-2) + ":" + ("0" + time.getMinutes()).slice(-2);

                let el_container = newDomNode('div', 'message');

                let el_time = newDomNode('div', 'time', time_repr);
                let el_user = newDomNode('div', 'user', message.username + ':');
                let el_message = newDomNode('div', 'message', message.message);

                el_container.appendChild(el_time);
                el_container.appendChild(el_user);
                el_container.appendChild(el_message);

                this.message_list.appendChild(el_container);
                this.message_list.scrollTop = this.message_list.scrollHeight;
            });
        }

        return ChatBox;

    })();

    let Connection = (() => {

        function Connection(on_receive_message) {

            let endpoint = this.getEndpoint();

            this.socket = new ReconnectingWebSocket(endpoint);
            this.socket.onopen    = (e) => this.onSocketOpen(e);
            this.socket.onmessage = (e) => this.onSocketMessage(e);
            this.socket.onerror   = (e) => this.onSocketError(e);
            this.socket.onclose   = (e) => this.onSocketClose(e);

            this.on_receive_message = on_receive_message;

        }

        Connection.prototype.getEndpoint = function getEndpoint() {
            let loc = window.location;
            let wsStart = loc.protocol == 'https' ? 'wss://' : 'ws://';
            return wsStart + loc.host + '/';
        }

        Connection.prototype.sendMessage = function sendMessage(thread_id, message) {

            var message_pack = {
                    'action': 'thread_message',
                    'params': {
                            'thread_id': thread_id,
                            'message': message
                        }
                }
            this.socket.send(JSON.stringify(message_pack));

        }

        Connection.prototype.onSocketOpen = function onSocketOpen(e) {
            console.log('socket opened', e);
        }

        Connection.prototype.onSocketMessage = function onSocketMessage(e) {
            var message_pack = JSON.parse(e.data);
            this.on_receive_message(message_pack);
        }

        Connection.prototype.onSocketError = function onSocketError(e) {
            console.log('socket error', e);
        }

        Connection.prototype.onSocketClose = function onSocketClose(e) {
            console.log('socket closed', e);
        }

        Connection.prototype.loadHistory = function loadHistory(thread_id, thread_url, on_loaded) {
            $.ajax({
                url: thread_url,
                dataType: 'json',
                success: function (data) {
                    if (data.thread_messages) {
                        on_loaded(data.thread_messages);
                    }
                }
            });
        }

        return Connection;

    })();


    let connection = new Connection((message_pack) => {
        chatbox.addMessages([message_pack]);
    });

    let chatbox = new ChatBox({
            message_form_selector: "#form",
            message_field_selector: "#chatmessage",
            message_list_selector: "#chat-messages",
            on_send_message: (thread_id, message) => connection.sendMessage(thread_id, message)
        });

    let thread_list = new ThreadList('.messenger > .thread-list > ul.thread-list > li', (thread_id, thread_url) => {
        chatbox.setThread(thread_id);
        chatbox.clearMessageList();
        connection.loadHistory(thread_id, thread_url, (messages) => {
            chatbox.addMessages(messages);
        });
    });

})(Utils);
