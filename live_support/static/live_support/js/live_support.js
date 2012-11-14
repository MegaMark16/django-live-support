var check_messages_interval = 2000;
var current_check_messages_interval = check_messages_interval;

$(document).ready(function() {
    // Bind events for changing the currently active chat and sending a message
    $('.chat_names a').click(changeChat);        
    $('.send_message_button').click(sendMessage);

    // show the first active chat and set its label to active
    $('.message_list:first:hidden').show();
    $('.chat_names a:first').addClass('selected');

    // Scroll all of the active chats to the bottom of the conversation
    scrollAll();

    // Set the timeout for pulling for new messages.
    setTimeout(getMessages, current_check_messages_interval);
});

// Check for new messages for any of the currently active chat sessions by
// passing the chat id and the id of the last message received for each chat
// session. Also update the list of pending chats.
function getMessages() {
    var args = {};
    $('.chat').each(function(index, item) {
        var chat_id = $(item).find('.chat_id').val();
        var last_message_control = $(item).find('.message_list li:last');
        // Are there any existing messages for this chat session? If so, grab
        // the id of the last message received.
        if (last_message_control.length > 0) {
            var last_message_id = $(item).find('.message_list li:last').attr('id').replace('message_', '');
            args[chat_id] = last_message_id;
        }
        else {
            args[chat_id] = 0;
        }
    });

    // document.get_messages_url is set in the template using a {% url %} tag
    var ajax_args = {
        url: document.get_messages_url, 
        data: args, 
        success: gotMessages, 
        error: getMessagesFailed,
        dataType: 'json'
    };
    // Make the call.
    $.ajax(ajax_args);
}

// If there was an error retrieving messages, we don't want to just keep
// hitting the server over and over again, so we make the interval double
// every time it continues to fail.  We set this interval value back to 
// the default as soon as a successful call goes through. 
function getMessagesFailed() {
    current_check_messages_interval = current_check_messages_interval * 2;
    // TODO: show a message ot the user letting them know that message
    // checking will be delayed by x seconds...
    setTimeout(getMessages, current_check_messages_interval);
}

// Handle the response from the server with the list of new messages for 
// each active chat session and the list of currently pending chat sessions.
function gotMessages(resp) { 
    // Weird thing, sometimes jQuery will call this method even when the
    // request failed, so if the resp is null we need to call getMessagesFailed
    if (resp == null) {
        getMessagesFailed();
        return;
    }
    // If the request was actually successful, reset the wait interval to 
    // the default wait time.
    current_check_messages_interval = check_messages_interval;

    // Loop through each active chat session and add all new messages to the 
    // message list for this chat session.
    for (var chat_id in resp.chats) {
        var chat = resp.chats[chat_id];
        var message_list = $('#chat_' + chat_id).find('ul');
        for (var index in chat.messages) {
            var message = chat.messages[index];
            var new_message_element = $( document.createElement('li'));
            if (message.name == '') {
                $(new_message_element).addClass('system_message');
                $(new_message_element).html(message.message);
            }
            else {
                $(new_message_element).html(message.name + ': ' + message.message);
            }
            $(new_message_element).attr('id', 'message_' + message.pk);
            $(message_list).append(new_message_element);
            // Add a "new_message" class to the current chat session label
            // if this chat session is not currently selected, that way 
            // the admin user can see that there are new messages.
            $('.chat_names a[href="' + chat_id + '"]:not(".selected")').addClass('new_message');
        }
        // If the session is active (based on recent requests by the user's 
        // browser for new messages) we will make sure that the "The user has 
        // disconnected" message is hidden.
        if (chat.alive) {
            // user still connected or reconnected
            $('#chat_' + chat_id + ' .status').hide();
        }
        else {
            // user timed out
            $('#chat_' + chat_id + ' .status').show();
        }
    }

    // Remove all of the existing Pending Chats and add only the ones
    // received in the response from the server.
    $('.pending_chats ul').children().remove();
    for (var index in resp.pending_chats) {
        var chat = resp.pending_chats[index];
        $('.pending_chats ul').append('<li><a class="' + chat.active  + '" href="' + chat.url + '">' + chat.name + '</a></li>');
    }

    // Scroll all of the chat sessions to the bottom of the message list.
    scrollAll();

    // Set the timeout to check for new messages in a few seconds.
    setTimeout(getMessages, current_check_messages_interval);
}

// Change the currently active chat session being displayed.
function changeChat(event) {
    $('.message_list').hide();
    $('.chat_names a').removeClass('selected');
    $(this).addClass('selected').removeClass('new_message');
    $('#chat_' + $(event.target).attr('href')).show();
    $('#chat_' + $(event.target).attr('href')).find('.message_box').focus();
    scrollAll();
    return false;
}

// Send the message (if there is one) for the currently active chat session.
function sendMessage(event) {
    var message = $(event.target).parent().find('.message_box').val();
    if (message.trim() != '') {
        var chat_id = $(event.target).parent().find('.chat_id').val();
        var url = $(event.target).parents('form').attr('action');
        var last_message_id = $(event.target).parents('.chat').find('.message_list li:last').attr('id').replace('message_', '');
        var args = {
            'message': message,
            'last_message_id': last_message_id,
            'chat_id': chat_id
        };
        $.post(url, args, messageSent, 'json');
    }
    return false;
}

// Message sent, and in the resp is a list of new messages from the server 
// (including the one you just sent). Add those messages to the message list
function messageSent(response, code) {
    if (code == 'success') {
        var chat_id = response[0].chat;
        var message_list = $('#chat_' + chat_id).find('ul');
        var message_box = $('#chat_' + chat_id).find('.message_box');
        $(message_box).val('');
        for (var index in response) {
            var message = response[index];
            var new_message_element = $( document.createElement('li'));
            $(new_message_element).html(message.name + ': ' + message.message);
            $(new_message_element).attr('id', 'message_' + message.pk);
            $(message_list).append(new_message_element);
        }
        // Scroll to the bottom of the message list.
        scrollAll();
    }
}

// Scroll all of the active chat sessions message lists to the bottom.
function scrollAll() {
    $('.message_list ul').each(function(index, control) {
        $(control).scrollTop($(control).attr('scrollHeight') - $(control).height());
    });
}

// Boilerplate jquery config stuff to make sure that ajax requests include
// the Django csrf token.
$(document).ajaxSend(function(event, xhr, settings) {
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = $.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    function sameOrigin(url) {
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    }
    function safeMethod(method) {
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    if (!safeMethod(settings.type) && sameOrigin(settings.url)) {
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    }
});
