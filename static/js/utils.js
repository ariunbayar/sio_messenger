(function() {

    let Utils = {

        escapeHtml: function escapeHtml(unsafe) {
                return unsafe
                    .replace(/&/g, "&amp;")
                    .replace(/</g, "&lt;")
                    .replace(/>/g, "&gt;")
                    .replace(/"/g, "&quot;")
                    .replace(/'/g, "&#039;");
            },

        domEl: function domEl(tag, attrs, innerText) {

            let el = document.createElement(tag);
            for (attr in attrs) {
                let value = attrs[attr];
                el.setAttribute(attr, value);
            }
            if (innerText) {
                let innerTextEscaped = Utils.escapeHtml(innerText);
                let elText = document.createTextNode(innerTextEscaped);
                el.appendChild(elText);
            }
            return el;

        },

        domEscapedText: function domEscapedText(text) {
                let textEscaped = Utils.escapeHtml(text);
                return document.createTextNode(textEscaped);
            },

        truncate: function truncate(text, limit) {
                return text.substring(0, limit) + (text.length > limit ? ' ...' : '');
            }

    };


    window.Utils = Utils;

})();
