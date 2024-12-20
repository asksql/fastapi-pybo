<script>
    import Router from "svelte-spa-router";
    import Navigation from "./components/Navigation.svelte";
    import AnswerModify from "./routes/AnswerModify.svelte";
    import Chatbot from "./routes/Chatbot.svelte";
    import Detail from "./routes/Detail.svelte";
    import Home from "./routes/Home.svelte";
    import QuestionCreate from "./routes/QuestionCreate.svelte";
    import QuestionModify from "./routes/QuestionModify.svelte";
    import UserCreate from "./routes/UserCreate.svelte";
    import UserLogin from "./routes/UserLogin.svelte";

    const routes = {
        "/": Home,
        "/detail/:question_id": Detail,
        "/question-create": QuestionCreate,
        "/user-create": UserCreate,
        "/user-login": UserLogin,
        "/question-modify/:question_id": QuestionModify,
        "/answer-modify/:answer_id": AnswerModify,
        "/chatbot": Chatbot,
    };
</script>

<Navigation />
<Router {routes} />
