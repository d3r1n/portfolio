import { render } from "solid-js/web";
import { lazy } from "solid-js";
import { Router } from "@solidjs/router";

import "virtual:uno.css";

const root = document.getElementById("root");

const routes = [
    {
        path: "/",
        component: lazy(() => import("./pages/home")),
    },
];

if (import.meta.env.DEV && !(root instanceof HTMLElement)) {
    throw new Error(
        "Root element not found. Did you forget to add it to your index.html? Or maybe the id attribute got misspelled?",
    );
}

render(() => <Router>{routes}</Router>, root!);
