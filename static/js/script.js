$(function() {

    let socket = io.connect('http://localhost:5000')

    let messageForm = $('#message-form')
    let messageBox = $('#message-box-input')
    let recipientBox = $('#message-box-recipient')
    let senderBox = $('#message-box-sender')
    let fileForm = $('#file-form')
    let fileInput = $('#file-input')

    socket.on('connect', function() {
        if(senderBox.val() === undefined) return
        socket.emit('update username sid', senderBox.val())
    })

    socket.on('send message', function(message) {
        $('.thread').append('<p><strong>' + message['sender'] + ': </strong>' + message['message'] + '</p>')
    })

    $('#login-form').submit(function(e) {
        e.preventDefault()
        let username = $('#username').val()
        let password = $('#password').val()
        login(username, password);
    })

    $('#logout-btn').on('click', function() {
        socket.emit('logout', senderBox.val(), function() {
            $.get('/server/logout', function() {
                location.href = '../'
            })
        })
    })

    function login(username, password) {
        $.post('/server/login', {
            'username': username,
            'password': password
        }, function(data){
            socket.emit('login', data, function(res) {
                username = res
                location.reload() 
             })
        })
    }

    $('#search_users_field').on('input', function() {
        user_query = $('#search_users_field').val()
        search_user(user_query)
    })

    messageForm.submit(function(e) {
        e.preventDefault()
        let message = messageBox.val()
        message = message.trim()
        let recipient = recipientBox.val()
        let sender = senderBox.val()
        messageBox.val('')
        if(message == '') {
            return
        }
        socket.emit('new message', {
            'sender': sender,
            'message': message,
            'recipient': recipient
        })
        $('.thread').append('<p><strong>' + sender + ': </strong>' + message + '</p>')
    })

    // fileForm.submit(function(e) {
    //     e.preventDefault()
    //     socket.emit('new file', fileInput.val())
    // })

    function search_user(query) {
        $.ajax({
            'type': 'POST',
            'url': '../server/search',
            'data': {'query': query},
            'success': function(data) {
                append_result_to_modal(data)
                RefreshAddUserEventListener()
            }
        })
    }
    
    function append_result_to_modal(result) {
        searched_users.innerHTML = ''
        html = ''
        for(let prop in result) {
            name = result[prop].first_name + ' ' + result[prop].last_name
            username = result[prop].username
            is_friends = result[prop].is_friends
            button_state = username + '">Add</button>'
            if(is_friends) {
                button_state = username + '" disabled>Added</button>'
            }
            html += '<ul class="list-group">' + 
                '<div class="list-group-item">' +
                    '<div class="d-flex w-100 justify-content-between">' +
                        '<div>' + name +
                        '<small class="username-result"> / ' + username + '</small></div>' +
                        '<button class="btn btn-primary btn-sm add-user-btn" data-username="' + 
                        button_state +
                    '</div>' +
                '</div>' +
            '</ul>'
        }
        searched_users.innerHTML = html
    }
    
    function add_user(username) {
        $.ajax({
            'type': 'POST',
            'url': '../server/add_contact',
            'data': {'username': username},
            'success': function(data) {
                console.log(data)
            }
        })
    }
    
    function RefreshAddUserEventListener() {
        $(".available-contacts .add-user-btn").off(); 
        $(".available-contacts .add-user-btn").on("click", function() {
            let username = $(this).attr('data-username')
            $(this).prop('disabled', true)
            $(this).html('Added')
            add_user(username)
        })
    }
})

