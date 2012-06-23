var check_messages_interval = 2000;
var current_check_messages_interval = check_messages_interval;

$(document).ready(function() {
    $('.chat_names a').click(changeChat);        
    $('.send_message_button').click(sendMessage);
    //$('.end_chat_button').click(endChat);
    $('.message_list:first').show();
    $('.chat_names a:first').addClass('selected');
    scrollAll();
    setTimeout(getMessages, current_check_messages_interval);
});

function getMessages() {
    var args = {};
    $('.chat').each(function(index, item) {
        var chat_id = $(item).find('.chat_id').val();
        var last_message_control = $(item).find('.message_list li:last');
        if (last_message_control.length > 0) {
            var last_message_id = $(item).find('.message_list li:last').attr('id').replace('message_', '');
            args[chat_id] = last_message_id;
        }
        else {
            args[chat_id] = 0;
        }
    });
    var ajax_args = {
        url: document.get_messages_url, 
        data: args, 
        success: gotMessages, 
        error: getMessagesFailed,
        dataType: 'json'
    };
    $.ajax(ajax_args);
}

function getMessagesFailed() {
    current_check_messages_interval = current_check_messages_interval * 2;
    // TODO: show a message ot the user letting them know that message
    // checking will be delayed by x seconds...
    setTimeout(getMessages, current_check_messages_interval);
}

function gotMessages(resp) { 
    if (resp == null) {
        getMessagesFailed();
        return;
    }
    current_check_messages_interval = check_messages_interval;
    for (var chat_id in resp.messages) {
        var messages = resp.messages[chat_id];
        var message_list = $('#chat_' + chat_id).find('ul');
        for (var index in messages) {
            var message = messages[index];
            var new_message_element = $( document.createElement('li'));
            $(new_message_element).html(message.fields.name + ': ' + message.fields.message);
            $(new_message_element).attr('id', 'message_' + message.pk);
            $(message_list).append(new_message_element);
            $('.chat_names a[href="' + chat_id + '"]:not(".selected")').addClass('new_message');
        }
        if (resp.alive) {
            // user still connected or reconnected
        }
        else {
            // user timed out
        }
    }
    scrollAll();
    setTimeout(getMessages, current_check_messages_interval);
}

function changeChat(event) {
    $('.message_list').hide();
    $('.chat_names a').removeClass('selected');
    $(this).addClass('selected').removeClass('new_message');
    $('#chat_' + $(event.target).attr('href')).show();
    $('#chat_' + $(event.target).attr('href')).find('.message_box').focus();
    scrollAll();
    return false;
}

function endChat(event) {
    var chat_id = $(event.target).parent().find('.chat_id').val();
    var url = $(event.target).parents('form').attr('end_chat_url');
    var args = {
        'end_chat': 'true',
    };
    $.post(url, args);
    
    return false;
}

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

function messageSent(response, code) {
    if (code == 'success') {
        var chat_id = response[0].fields.chat;
        var message_list = $('#chat_' + chat_id).find('ul');
        var message_box = $('#chat_' + chat_id).find('.message_box');
        $(message_box).val('');
        for (var index in response) {
            var message = response[index];
            var new_message_element = $( document.createElement('li'));
            $(new_message_element).html(message.fields.name + ': ' + message.fields.message);
            $(new_message_element).attr('id', 'message_' + message.pk);
            $(message_list).append(new_message_element);
        }
        scrollAll();
    }
}

function scrollAll() {
    $('.message_list ul').each(function(index, control) {
        $(control).scrollTop($(control).attr('scrollHeight') - $(control).height());
    });
}

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
