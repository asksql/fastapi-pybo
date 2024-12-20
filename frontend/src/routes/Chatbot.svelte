<script>
    import { writable } from "svelte/store";

    let userMessage = "";
    let chatLog = writable([]);

    const sendMessage = async () => {
        if (userMessage.trim()) {
            chatLog.update((log) => [
                ...log,
                { sender: "user", message: userMessage },
            ]);
            const response = await fetch("http://localhost:8000/chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ message: userMessage }),
            });

            if (response.ok) {
                const data = await response.json();
                chatLog.update((log) => [
                    ...log,
                    { sender: "bot", message: data.reply },
                ]);
            } else {
                chatLog.update((log) => [
                    ...log,
                    {
                        sender: "bot",
                        message: "Error: Unable to fetch response",
                    },
                ]);
            }

            userMessage = "";
        }
    };
</script>

<div class="chat-container shadow">
    <div class="chat-log">
        {#each $chatLog as { sender, message }}
            <div class="chat-message {sender}">
                <div class="message {sender} shadow-sm">{message}</div>
            </div>
        {/each}
    </div>

    <div class="input-container">
        <input
            type="text"
            class="form-control"
            bind:value={userMessage}
            placeholder="Type your message here..."
            on:keypress={(e) => e.key === "Enter" && sendMessage()}
        />

        <button class="btn btn-primary" on:click={sendMessage}>Send</button>
    </div>
</div>

<style>
    .chat-container {
        width: 100%;
        max-width: 600px;
        margin: 20px auto;
        display: flex;
        flex-direction: column;
        border: 1px solid #dee2e6;
        border-radius: 0.375rem;
        overflow: hidden;
    }

    .chat-log {
        flex-grow: 1;
        padding: 1rem;
        overflow-y: auto;
        background-color: #f8f9fa;
        border-bottom: 1px solid #dee2e6;
    }

    .chat-message {
        margin-bottom: 1rem;
        display: flex;
    }

    .chat-message.user {
        justify-content: flex-end;
    }

    .chat-message.bot {
        justify-content: flex-start;
    }

    .message {
        max-width: 70%;
        padding: 0.75rem 1rem;
        border-radius: 0.375rem;
        font-size: 1rem;
    }

    .message.user {
        background-color: #007bff;
        color: #fff;
    }

    .message.bot {
        background-color: #e9ecef;
        color: #212529;
    }

    .input-container {
        padding: 0.75rem;
        background-color: #ffffff;
        display: flex;
        gap: 0.5rem;
        align-items: center;
    }

    input[type="text"] {
        flex-grow: 1;
        padding: 0.5rem 1rem;
        font-size: 1rem;
        border: 1px solid #ced4da;
        border-radius: 0.375rem;
        outline: none;
    }

    button {
        padding: 0.5rem 1rem;
        font-size: 1rem;
        border: none;
        border-radius: 0.375rem;
        background-color: #007bff;
        color: #ffffff;
        cursor: pointer;
        transition: background-color 0.2s;
    }

    button:hover {
        background-color: #0056b3;
    }
</style>
