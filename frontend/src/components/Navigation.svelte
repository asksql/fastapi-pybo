<script>
    import { link } from "svelte-spa-router";
    import {
        access_token,
        is_login,
        keyword,
        page,
        username,
    } from "../lib/store";
</script>

<nav class="navbar navbar-expand-lg navbar-light bg-light border-bottom">
    <div class="container-fluid">
        <a
            use:link
            class="navbar-brand"
            href="/"
            on:click={() => {
                ($keyword = ""), ($page = 0);
            }}>Pybo</a
        >
        <button
            class="navbar-toggle"
            type="button"
            data-bs-toggle="collapse"
            data-bs-target="#navbarSupportedContent"
            aria-controls="navbarSupportedContent"
            aria-expanded="false"
            aria-label="Toggle navigation"
        >
            <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarSupportedContent">
            <ul class="navbar-nav me-auto mb-2 mb-lg-0">
                {#if $is_login}
                    <li class="nav-item">
                        <a
                            use:link
                            class="nav-link"
                            href="/user-login"
                            on:click={() => {
                                $access_token = "";
                                $username = "";
                                $is_login = false;
                            }}>로그아웃({$username})</a
                        >
                    </li>
                {:else}
                    <li class="nav-item">
                        <a use:link class="nav-link" href="/user-create"
                            >회원가입</a
                        >
                    </li>
                    <li class="nav-item">
                        <a use:link class="nav-link" href="/user-login"
                            >로그인</a
                        >
                    </li>
                {/if}
                <li class="nav-item">
                    <a use:link class="nav-link" href="/chatbot"
                        ><strong>AI에게 물어보기</strong></a
                    >
                </li>
            </ul>
        </div>
    </div>
</nav>
