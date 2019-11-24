(function(Utils){

    let UserList = (() => {

        function UserList(config) {

            let searchbox = document.querySelector(config.searchbox_selector);
            let user_list_container = document.querySelector(config.user_list_selector);
            let user_list = Array.from(user_list_container.children);
            let user_list_title = document.querySelector(config.user_list_title_selector);

            this.users = [];
            this.user_list_container = user_list_container;
            this.user_list_title = user_list_title;

            this.onUserSelected = config.onUserSelected;

            user_list.forEach((el) => {
                this.users.push({
                    user_id: parseInt(el.getAttribute('data-id')),
                    search_text: el.getAttribute('data-search'),
                    element: el
                });
                el.addEventListener('click', (e) => {
                    let user_id = parseInt(e.target.getAttribute('data-id'));
                    this.onUserSelected(user_id);
                })
            });

            this.searchTimeout = 0;

            searchbox.addEventListener('keydown', (e) => {
                if (this.searchTimeout) {
                    clearTimeout(this.searchTimeout);
                }
                setTimeout(() => {
                    let val = e.target.value;
                    if (val && val.length > 1) {
                        this.filter(val);
                    } else {
                        this.hide();
                    }
                }, 350);
            });
        }

        UserList.prototype.hide = function hide() {

            this.user_list_title.classList.toggle('hidden', true);
            this.user_list_container.classList.toggle('hidden', true);

        }

        UserList.prototype.filter = function filter(search) {

            let isFound = false;

            this.users.forEach((user) => {
                var start = user.search_text.toLowerCase().indexOf(search.toLowerCase());
                user.element.classList.toggle('hidden', start === -1);
                isFound = isFound || start > -1;
            });

            this.user_list_title.classList.toggle('hidden', !isFound);
            this.user_list_container.classList.toggle('hidden', !isFound);

        }

        return UserList;

    })();

    let ThreadList = (() => {

        function ThreadList(container_selector, fn_thread_selected) {

            this.active_thread_id = null;
            this.active_child_element = null;

            this.child_elements = {};

            this.on_thread_selected = fn_thread_selected;

            this.container = document.querySelector(container_selector);

            Array.from(this.container.children).forEach((child_element) => {

                let thread_id = parseInt(child_element.getAttribute('data-thread-id'));
                this.child_elements[thread_id] = child_element;

                child_element.addEventListener('click', (e) => {
                    this.activate(thread_id);
                });

            });
        }

        ThreadList.prototype.create = function create(thread_detail) {

            let attrs = {
                'data-thread-id': thread_detail.id,
                'data-thread-history': thread_detail.url,
            }
            let thread_item = Utils.domEl('li', attrs, thread_detail.name);

            this.container.appendChild(thread_item);

            thread_item.appendChild(Utils.domEl('div', {'class': 'last-message'}));

            this.child_elements[thread_detail.id] = thread_item;
            thread_item.addEventListener('click', (e) => {
                this.activate(thread_detail.id);
            });

        }

        ThreadList.prototype.activate = function activate(thread_id) {

            let child_element = this.child_elements[thread_id];

            if (this.active_child_element === child_element) {
                return;
            }

            if (this.active_child_element) {
                this.active_child_element.classList.remove('active');
            }
            child_element.classList.add('active');
            this.active_child_element = child_element;
            this.active_thread_id = thread_id;

            let thread_url = child_element.getAttribute('data-thread-history');

            this.on_thread_selected(thread_id, thread_url);
        };

        ThreadList.prototype.setLatestMessages = function setLatestMessages(message_packs) {

            message_packs.forEach((message_pack) => {

                if (this.active_thread_id == message_pack.thread_id) return;

                let el = this.child_elements[message_pack.thread_id];

                let elLastMessage = el.querySelector('.last-message');
                let lastMessage = message_pack.username + ': ' + message_pack.message;

                lastMessage = Utils.truncate(lastMessage, 45);

                elLastMessage.innerHTML = '';
                elLastMessage.appendChild(Utils.domEscapedText(lastMessage));

            });

        }

        ThreadList.prototype.setLastMessageSeen = function setLastMessageSeen(thread_id) {
            let el = this.child_elements[thread_id];
            el.querySelector('.last-message').innerHTML = '';
        }

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
            this.user_ids = [];
            this.on_send_message = config.on_send_message;
            this.message_form = message_form;
            this.message_list = message_list;

        }

        ChatBox.prototype.sendMessage = function sendMessage(message) {

            if (this.thread_id === null && this.user_ids.length == 0) {
                return;
            }

            this.on_send_message(this.thread_id, this.user_ids, message);

        }

        ChatBox.prototype.newGroupChat = function newGroupChat(user_ids) {

            this.clearMessageList();
            this.clearFormValues();
            this.thread_id = null;
            this.user_ids = user_ids;

        }

        ChatBox.prototype.setThread = function setThread(thread_id) {

            this.thread_id = thread_id;

        }

        ChatBox.prototype.clearMessageList = function clearMessageList() {
            while (this.message_list.firstChild) {
                this.message_list.removeChild(this.message_list.firstChild);
            }
        }

        ChatBox.prototype.clearFormValues = function clearFormValues() {
            this.message_form.reset();
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

                if (this.thread_id === null) return;
                if (this.thread_id != message.thread_id) return;

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

        Connection.prototype.threadCreate = function threadCreate(user_ids, message) {

            var user_message_pack = {
                    'action': 'thread_create',
                    'params': {
                        'user_ids': user_ids,
                        'message': message,
                    }
                }
            this.socket.send(JSON.stringify(user_message_pack));

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


    let connection = new Connection((server_message) => {

        if (server_message.action == 'thread_message') {

            chatbox.addMessages([server_message]);
            thread_list.setLatestMessages([server_message]);

        } else if (server_message.action == 'thread_create') {

            thread_list.create(server_message);

        }

    });

    let chatbox = new ChatBox({
            message_form_selector: "#form",
            message_field_selector: "#chatmessage",
            message_list_selector: "#chat-messages",
            on_send_message: (thread_id, user_ids, message) => {
                if (thread_id) {
                    connection.sendMessage(thread_id, message);
                } else if (user_ids.length) {
                    connection.threadCreate(user_ids, message);
                }
            }
        });

    let thread_list = new ThreadList('.messenger > .thread-list > ul.thread-list', (thread_id, thread_url) => {
        chatbox.setThread(thread_id);
        chatbox.clearMessageList();
        chatbox.clearFormValues();
        connection.loadHistory(thread_id, thread_url, (messages) => {
            chatbox.addMessages(messages);
            thread_list.setLastMessageSeen(thread_id);
        });
    });

    let user_list = new UserList({
        searchbox_selector: '.messenger > .thread-list >#user-search',
        user_list_selector: '.messenger > .thread-list > ul.user-list',
        user_list_title_selector: '.messenger > .thread-list > .user-list-title',
        onUserSelected: (user_id) => {
            chatbox.newGroupChat([user_id]);
        }
    });

})(Utils);
