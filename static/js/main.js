document.addEventListener('DOMContentLoaded', () => {
    const socket = io();

    // UI Elements
    const loginScreen = document.getElementById('login-screen');
    const lobbyActions = document.getElementById('lobby-actions');
    const joinInputs = document.getElementById('join-inputs');
    const usernameInput = document.getElementById('username');
    const roomCodeInput = document.getElementById('room-code-input');

    const btnCreate = document.getElementById('btn-create-server');
    const btnShowJoin = document.getElementById('btn-show-join');
    const btnJoinServer = document.getElementById('btn-join-server');
    const btnBackLobby = document.getElementById('btn-back-lobby');

    const chatInterface = document.getElementById('chat-interface');
    const chatWindow = document.getElementById('chat-window');
    const userList = document.getElementById('user-list');
    const headerStatus = document.querySelector('.terminal-text');

    const messageInput = document.getElementById('message-input');
    const btnSend = document.getElementById('btn-send');
    const fileInput = document.getElementById('file-input');
    const secureOptions = document.getElementById('secure-options');
    const encryptPass = document.getElementById('encrypt-pass');

    // Modals
    const decryptModal = document.getElementById('decrypt-modal');
    const decryptedContent = document.getElementById('decrypted-content');
    const closeModal = document.querySelector('.close-modal');

    const authModal = document.getElementById('auth-modal');
    const decryptPassInput = document.getElementById('decrypt-pass');
    const btnDecryptConfirm = document.getElementById('btn-decrypt-confirm');
    const closeAuth = document.getElementById('close-auth');

    let username = '';
    let currentPendingUrl = '';

    // --- Lobby Logic ---
    btnShowJoin.addEventListener('click', () => {
        lobbyActions.classList.add('hidden');
        joinInputs.classList.remove('hidden');
    });

    btnBackLobby.addEventListener('click', () => {
        joinInputs.classList.add('hidden');
        lobbyActions.classList.remove('hidden');
    });

    btnCreate.addEventListener('click', () => {
        const user = usernameInput.value.trim();
        if (!user) return alert("CODENAME REQUIRED");
        username = user;
        socket.emit('create_server', { username: username });
    });

    btnJoinServer.addEventListener('click', () => {
        const user = usernameInput.value.trim();
        const code = roomCodeInput.value.trim();
        if (!user || !code) return alert("CREDENTIALS MISSING");
        username = user;
        socket.emit('join_server', { username: username, code: code });
    });

    // --- Socket Events ---
    socket.on('server_created', (data) => {
        enterChat(data.code, true);
    });

    socket.on('server_joined', (data) => {
        enterChat(data.code, data.admin);
    });

    socket.on('error', (data) => {
        alert("ERROR: " + data.msg);
    });

    socket.on('user_list', (data) => {
        updateUserList(data.users);
    });

    socket.on('kicked', (data) => {
        alert(data.msg);
        location.reload();
    });

    socket.on('remove_node', (data) => {
        const el = document.getElementById(`msg-${data.id}`);
        if (el) {
            el.style.opacity = '0';
            setTimeout(() => el.remove(), 1000); // Fade out then remove
        }
    });

    socket.on('message', (data) => addMessage(data, 'text'));
    socket.on('ghost_image', (data) => addMessage(data, 'image'));
    socket.on('status', (data) => addSystemMessage(data.msg));
    socket.on('connect', () => console.log('Connected'));

    socket.on('decryption_result', (data) => {
        if (data.error) {
            alert(data.message);
        } else {
            authModal.classList.add('hidden');
            showDecryptedContent(data.message);
        }
    });

    function enterChat(code, isAdmin) {
        loginScreen.classList.add('hidden');
        chatInterface.classList.remove('hidden');
        headerStatus.innerText = `NET_STATUS: SECURE // NODE: ${code} // ROLE: ${isAdmin ? 'ADMIN' : 'OPERATIVE'}`;

        // Add Copy functionality
        headerStatus.style.cursor = "pointer";
        headerStatus.title = "CLICK TO COPY FREQUENCY CODE";
        headerStatus.onclick = () => {
            navigator.clipboard.writeText(code);
            addSystemMessage(`FREQUENCY CODE ${code} COPIED TO CLIPBOARD.`);
        };
    }

    function updateUserList(users) {
        userList.innerHTML = '';
        users.forEach(u => {
            const li = document.createElement('li');
            li.className = 'user-item';

            let html = `<span class="${u.username === username ? 'you' : ''}">${u.username} ${u.is_admin ? '[ADMIN]' : ''}</span>`;

            if (u.username !== username) {
                html += `<button class="btn-kick" onclick="kickUser('${u.sid}')">KICK</button>`;
            }
            li.innerHTML = html;
            userList.appendChild(li);
        });
    }

    window.kickUser = (sid) => {
        if (confirm("EJECT THIS OPERATIVE?")) {
            socket.emit('kick_user', { target_sid: sid });
        }
    };

    // --- Chat & Secure Logic ---
    fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) {
            messageInput.placeholder = "ENTER SECRET PAYLOAD FOR IMAGE...";
            secureOptions.classList.remove('hidden');
            encryptPass.focus();
            addSystemMessage("IMAGE ARTIFACT LOADED. INPUT ENCRYPTION PASSPHRASE.");
        } else {
            secureOptions.classList.add('hidden');
        }
    });

    btnSend.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') sendMessage(); });
    encryptPass.addEventListener('keypress', (e) => { if (e.key === 'Enter') sendMessage(); });

    function sendMessage() {
        if (fileInput.files.length > 0) {
            // Secure Image Send
            const passphrase = encryptPass.value.trim();
            const isSelfDestruct = document.getElementById('self-destruct-check').checked;

            if (!passphrase) return alert("ENCRYPTION PASSPHRASE REQUIRED");

            const file = fileInput.files[0];
            const reader = new FileReader();
            reader.onload = function (evt) {
                const secretText = messageInput.value.trim() || "NO_DATA";

                socket.emit('secure_image', {
                    image: evt.target.result,
                    secret_text: secretText,
                    passphrase: passphrase,
                    is_self_destruct: isSelfDestruct
                });

                // Reset
                fileInput.value = '';
                messageInput.value = '';
                encryptPass.value = '';
                document.getElementById('self-destruct-check').checked = false;
                secureOptions.classList.add('hidden');
                messageInput.placeholder = "TRANSMIT DATA...";
                addSystemMessage("ENCRYPTING AND TRANSMITTING...");
            };
            reader.readAsDataURL(file);
        } else {
            // Text Message
            const msg = messageInput.value.trim();
            const isFlash = document.getElementById('flash-mode-check').checked;
            if (msg) {
                socket.emit('message', { msg: msg, is_flash: isFlash });
                messageInput.value = '';
                document.getElementById('flash-mode-check').checked = false;
            }
        }
    }

    // --- Display Logic ---
    function addSystemMessage(msg) {
        const div = document.createElement('div');
        div.className = 'system-msg';
        div.innerText = `>> ${msg}`;
        chatWindow.appendChild(div);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }

    function addMessage(data, type) {
        const div = document.createElement('div');
        const isSelf = data.username === username;
        div.className = `message ${isSelf ? 'self' : ''} ${type === 'image' ? 'ghost' : ''}`;

        if (data.id) div.id = `msg-${data.id}`; // Assign ID for deletion

        const meta = document.createElement('div');
        meta.style.fontSize = '0.8rem';
        meta.style.color = '#777';
        meta.innerText = `${data.username} [${data.timestamp}]`;
        div.appendChild(meta);

        if (type === 'text') {
            const text = document.createElement('div');
            text.innerText = data.msg;
            if (data.is_flash) {
                text.className = 'redacted';
                text.title = "HOVER TO DECRYPT";
            }
            div.appendChild(text);
        } else if (type === 'image') {
            const img = document.createElement('img');
            img.src = data.url;
            img.className = 'ghost-image';
            img.title = "ENCRYPTED SIGNAL DETECTED";

            // Store metadata on the element for retrieval when clicking
            img.dataset.url = data.url;
            img.dataset.id = data.id;
            img.dataset.selfDestruct = data.is_self_destruct;

            img.onclick = () => requestDecryptionAuth(img.dataset);
            div.appendChild(img);

            const hint = document.createElement('div');
            hint.innerText = data.is_self_destruct ? ">> SELF-DESTRUCT SEQUENCE ARMED" : ">> LOCKED SIGNAL";
            hint.style.fontSize = "0.7rem";
            hint.style.color = "var(--razer-red)";
            div.appendChild(hint);
        }

        chatWindow.appendChild(div);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }

    // --- Decryption Flow ---
    let currentArtifactId = null;
    let currentIsSelfDestruct = false;

    function requestDecryptionAuth(dataset) {
        currentPendingUrl = dataset.url;
        currentArtifactId = dataset.id;
        currentIsSelfDestruct = (dataset.selfDestruct === 'true');

        authModal.classList.remove('hidden');
        decryptPassInput.value = '';
        decryptPassInput.focus();
    }

    btnDecryptConfirm.addEventListener('click', () => {
        const pass = decryptPassInput.value.trim();
        if (pass) {
            socket.emit('decrypt_request', { url: currentPendingUrl, passphrase: pass });
        }
    });

    function showDecryptedContent(text) {
        decryptedContent.innerText = text;
        decryptModal.classList.remove('hidden');

        // If self destruct is active for this message, start timer when they VIEW it or when they CLOSE it? 
        // User asked for "30 seconds after message was opend and closed". 
        // So we attach logic to the close event.
    }

    [closeModal, closeAuth].forEach(el => el.addEventListener('click', () => {
        const wasDecryptModal = !decryptModal.classList.contains('hidden');

        decryptModal.classList.add('hidden');
        authModal.classList.add('hidden');

        if (wasDecryptModal && currentIsSelfDestruct && currentArtifactId) {
            addSystemMessage(`⚠ SELF-DESTRUCT INITIATED FOR ARTIFACT ${currentArtifactId.substr(-4)}... 30 SECONDS.`);
            // Capture these in closure
            const targetId = currentArtifactId;
            setTimeout(() => {
                socket.emit('delete_artifact', { id: targetId });
            }, 30000); // 30 seconds

            // Reset
            currentArtifactId = null;
            currentIsSelfDestruct = false;
        }
    }));


    window.onclick = function (event) {
        if (event.target == decryptModal) decryptModal.classList.add('hidden');
        if (event.target == authModal) authModal.classList.add('hidden');
    }
});
