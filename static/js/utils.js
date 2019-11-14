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
