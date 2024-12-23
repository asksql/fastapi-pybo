<script>
    import { writable } from "svelte/store";
    import fastapi from "../lib/api";

    let userMessage = "";
    let chatLog = writable([]);

    const sendMessage = async () => {
        if (userMessage.trim()) {
            let userMessageObj = { sender: "user", message: userMessage };
            chatLog.update((log) => [...log, userMessageObj]);

            // FastAPI 호출
            fastapi(
                "post",
                "/api/chat/req",
                { sender: "user", message: userMessage },
                (json) => {
                    typeMessage(json.reply);
                },
                (err_json) => {
                    chatLog.update((log) => [
                        ...log,
                        {
                            sender: "bot",
                            message: "Error: Unable to fetch response",
                        },
                    ]);
                }
            );

            userMessage = "";
        }
    };

    // 타이핑 효과를 추가하는 함수
    const typeMessage = (fullMessage) => {
        let currentMessage = "";
        let index = 0;

        const typeInterval = setInterval(() => {
            if (index < fullMessage.length) {
                currentMessage += fullMessage[index];
                index++;

                // 업데이트된 메시지를 반영
                chatLog.update((log) => {
                    // 마지막 메시지가 "bot"인지 확인
                    const updatedLog = [...log];
                    if (updatedLog[updatedLog.length - 1]?.sender === "bot") {
                        updatedLog[updatedLog.length - 1].message =
                            currentMessage;
                    } else {
                        updatedLog.push({
                            sender: "bot",
                            message: currentMessage,
                        });
                    }
                    return updatedLog;
                });
            } else {
                clearInterval(typeInterval); // 타이핑 완료 후 정리
            }
        }, 50); // 각 글자 타이핑 속도 (50ms)
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
    /* 기존 스타일 유지 */
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
