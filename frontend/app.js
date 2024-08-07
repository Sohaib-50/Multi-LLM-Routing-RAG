const ai_models = [];
document.addEventListener('DOMContentLoaded', () => {

    const app = document.getElementById('app');

    document.getElementById('new-chat-form').addEventListener('submit', create_new_chat);
    document.getElementById('new-message-form').addEventListener('submit', get_ai_response);
    load_chats();
    load_models_info();

    // asynchrnous call to get all models
    get_all_models()
        .then(models => {
            ai_models.push(...models);
            populate_update_model_selects();
            document.getElementById('update-models-form').addEventListener('submit', update_models);
        });

    console.log('Document loaded');

});


function get_csrf_token() {
    for (let cookie of document.cookie.split(';')) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') {
            console.log('CSRF token:', value);
            return value;
        }
    }
    console.error('CSRF token not found');
    return '';
}


function spinner_component() {
    const spinner = document.createElement('span');
    spinner.classList.add('spinner-border', 'spinner-border-sm');
    spinner.setAttribute('role', 'status');
    spinner.setAttribute('aria-hidden', 'true');
    return spinner;
}


function message_component(message) {
    if (message.role === 'assistant') {
        message.role = 'ai';
    }

    let containerDiv = document.createElement('div');
    containerDiv.className = `message ${message.role}`;
    containerDiv.addEventListener('click', () => {
        show_message_metadata(JSON.stringify(message, null, 4));
    }
    );

    containerDiv.innerHTML = `
        <div class="author">${message.role}</div>
        <pre style="white-space: pre-wrap;" class="content">${marked.parse(message.content)}</pre>
    `;


    return containerDiv;
}


function show_message_metadata(message_metadata_json) {

    const metadata_modal = document.getElementById('message-metadata-modal');
    const metadata_modal_body = metadata_modal.querySelector('.modal-body');
    metadata_modal_body.innerHTML = `
        <pre>${message_metadata_json}</pre>
    `;

    $('#message-metadata-modal').modal('show');

}


function load_chats() {
    const url = '/api/chats';
    const chats_list_div = document.getElementById('chats-list');

    fetch(url)
        .then(response => response.json())
        .then(data => {
            // console.log(`Fetched chats:\n${JSON.stringify(data)}`);
            chats_list_div.innerHTML = '';

            data.chats.forEach(chat => {
                const chat_item = document.createElement('div');
                chat_item.classList.add('chat-item');
                chat_item.dataset.id = chat.id;
                chat_item.innerHTML = `
                    <b> ${chat.name} </b>
                    <div class="chat-date">${chat.started_at}</div>
                `;
                // add event listener to load chat messages (call load_chat)
                chat_item.addEventListener('click', () => {
                    load_chat(chat.id);
                });
                chats_list_div.appendChild(chat_item);
            });
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

function load_models_info(models_info = null) {
    if (models_info) {
        document.querySelector('#strong-model-name').innerHTML = models_info.strong_model_name;
        document.querySelector('#weak-model-name').innerHTML = models_info.weak_model_name;
        return;
    }

    const url = '/api/models_info';

    fetch(url)
        .then(response => response.json())
        .then(data => {
            console.log('Fetched models info:', data);

            document.querySelector('#strong-model-name').innerHTML = data.strong_model_name;
            document.querySelector('#weak-model-name').innerHTML = data.weak_model_name;
        })
        .catch(error => {
            console.error('Error:', error);
        });
}


function get_all_models() {
    const url = '/api/all_models';

    return fetch(url)
        .then(response => response.json())
        .then(data => {
            console.log('Fetched all models:', data);
            return data.models || [];
        })
        .catch(error => {
            console.error('Error in fetching all models:', error);
            return [];
        });
}

function populate_update_model_selects() {
    const strong_model_select = document.getElementById('new-strong-model-name');
    const weak_model_select = document.getElementById('new-weak-model-name');

    // add option for each model
    ai_models.forEach(model => {
        const option = document.createElement('option');
        option.value = model;
        option.textContent = model;
        strong_model_select.appendChild(option);
        weak_model_select.appendChild(option.cloneNode(true));
    });
}

function update_models(event) {
    event.preventDefault();

    const form = event.target;
    const new_strong_model_name = form.querySelector('select[name="new-strong-model-name"]').value;
    const new_weak_model_name = form.querySelector('select[name="new-weak-model-name"]').value;

    if (new_strong_model_name === new_weak_model_name) {
        alert('Strong and weak models must be different.');
        return;
    }

    const url = '/api/models_info/';
    
    fetch(url, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': get_csrf_token(),
        },
        body: JSON.stringify({
            strong_model_name: new_strong_model_name,
            weak_model_name: new_weak_model_name,
        }),
    })
        .then(response => {
            console.log('Response status:', response.status);

            if (!response.ok) {
                return response.json().then(errorData => {
                    throw new Error(`Error ${response.status}: ${errorData.message || response.statusText}`);
                });
            }

            return response.json();
        })
        .then(data => {
            console.log('Models updated:', data);

            load_models_info(data);

            // close modal
            $('#update-models-modal').modal('hide');
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred, please try again.');
        });
}


function load_chat(chat_id) {
    console.log(`Loading chat with id: ${chat_id}`);
    const url = `/api/chat/${chat_id}`;

    const chat_interface = document.getElementById('chat-interface');
    const chat_header = chat_interface.querySelector('#chat-header');
    const chat_id_field = chat_interface.querySelector('input[name="chat-id"]');
    const chat_messages = chat_interface.querySelector('#chat-messages');

    // clear chat messages
    chat_messages.innerHTML = '';

    fetch(url, {
        method: 'GET',
        headers: {
            'X-CSRFToken': get_csrf_token(),
        },
    })
        .then(response => {
            console.log('Response status:', response.status);

            if (!response.ok) {
                return response.json().then(errorData => {
                    throw new Error(`Error ${response.status}: ${errorData.message || response.statusText}`);
                });
            }

            return response.json();
        }
        )
        .then(data => {
            console.log('Chat data:', data);

            chat_header.innerHTML = `
                <h2>${data.name}</h2>
            `;

            data.messages.forEach(message => {
                chat_messages.appendChild(message_component(message));
            });

            chat_id_field.value = chat_id;

            chat_messages.scrollTop = chat_messages.scrollHeight;
        }
        )
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred, please try again.');
        }
        );

}

function create_new_chat(event) {
    event.preventDefault();

    const url = '/api/create_chat/';
    const form = event.target;
    const submit_button = form.querySelector('button[type="submit"]');
    const submit_button_text = submit_button.innerHTML;

    // add a loading spinner and message to the submit button
    submit_button.innerHTML = `
        ${spinner_component().outerHTML}
        Creating chat, stay on this page...
    `;

    const form_data = new FormData();
    form_data.append('name', form.querySelector('input[name="new-chat-name"]').value);
    form_data.append('knowledgebase', form.querySelector('textarea[name="new-chat-knowledgebase"]').value);

    // debug logs
    console.log('Creating new chat...');
    console.log('Form data:', form_data);

    fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': get_csrf_token(),
        },
        body: form_data,
    })
        .then(response => {
            console.log('Response status:', response.status);

            if (!response.ok) {
                return response.json().then(errorData => {
                    throw new Error(`Error ${response.status}: ${errorData.message || response.statusText}`);
                });
            }

            return response.json();
        })
        .then(data => {
            console.log('New chat created:', data);

            // reset form
            submit_button.innerHTML = submit_button_text;
            form.querySelector('input[name="new-chat-name"]').value = '';
            form.querySelector('textarea[name="new-chat-knowledgebase"]').value = '';

            // load new chat and update chats list
            load_chat(data.chat_id);
            load_chats();

            // close modal
            $('#new-chat-modal').modal('hide');

        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred, please try again.');

            // reset form
            submit_button.innerHTML = submit_button_text

        });
}


function get_ai_response(event) {

    console.log("CSRF IS ---------->", get_csrf_token());
    event.preventDefault();

    const form = event.target;
    const form_data = new FormData();
    const chat_id = form.querySelector('input[name="chat-id"]').value;
    form_data.append('chat_id', chat_id);
    form_data.append('query', form.querySelector('textarea[name="new-message"]').value);
    form_data.append('optimization_metric', form.querySelector('select[name="optimization-metric"]').value);

    console.log("Optimization metric: ", form.querySelector('select[name="optimization-metric"]').value);

    const url = `/api/chat/${chat_id}/get_ai_response/`;
    console.log('url:', url, 'chat_id:', chat_id);
    const submit_button = form.querySelector('button[type="submit"]');
    const submit_button_text = submit_button.innerHTML;

    // add a loading spinner to submit button and disable it
    submit_button.innerHTML = `
        ${spinner_component().outerHTML}
    `;
    submit_button.disabled = true;

    // debug logs
    console.log('Getting AI response...');
    console.log('Form data:', form_data);

    fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': get_csrf_token(),
        },
        body: form_data,
    })
        .then(response => {
            console.log('Response status:', response.status);

            if (!response.ok) {
                return response.json().then(errorData => {
                    throw new Error(`Error ${response.status}: ${errorData.message || response.statusText}`);
                });
            }

            return response.json();
        })
        .then(data => {
            console.log('AI response data:', data);

            // reset form
            submit_button.innerHTML = submit_button_text;
            submit_button.disabled = false;
            form.querySelector('textarea[name="new-message"]').value = '';

            // add user message to chat messages
            const chat_messages = document.getElementById('chat-messages');
            chat_messages.appendChild(message_component(data.user_message));

            // add AI response to chat messages
            chat_messages.appendChild(message_component(data.ai_message));
            //     chat_messages.innerHTML += `
            //     <div class="message user">
            //         <div class="author">user</div>
            //         ${data.query}
            //     </div>
            // `;

            // // add AI response to chat messages
            // chat_messages.innerHTML += `
            //     <div class="message ai">
            //         <div class="author">ai</div>
            //         ${data.response}
            //     </div>
            // `;

            // scroll to bottom of chat messages
            chat_messages.scrollTop = chat_messages.scrollHeight;

        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred, please try again.');

            // reset form
            submit_button.innerHTML = submit_button_text;
            submit_button.disabled = false;
        });



}