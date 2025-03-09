import LinkedIn from "iconoir/icons/regular/linkedin.svg?raw";
import GitHub from "iconoir/icons/regular/github.svg?raw";
import Link from "iconoir/icons/regular/link.svg?raw";

let linkStyle =
    "flex items-center justify-center min-h-10 min-w-10 border-rd-md *:size-8 color-white shadow-md shadow-stone-900/30";

let colorsLinkedin = "bg-[#0072b1]";
let colorsGithub = "bg-stone-950";
let colorsDevto = "bg-green-600";

let img =
    "url(https://images.unsplash.com/photo-1605915034248-ba76b2f32c3c?q=80&w=3168&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D)";

function joinClasses(classArray: Array<string>): string {
    return classArray.join(" ");
}

// @ts-ignore
export default function Profile(props) {
    return (
        <div
            class={joinClasses([
                "profile flex items-center justify-between",
                props.classExtra,
            ])}
        >
            <div
                id="profile-image"
                class="size-64 border-rd-md ml-4 outline-solid outline-2 outline-stone-50/50 outline-offset-2 shadow-lg shadow-indigo-600/40 opacity-90"
                style:background-image={img}
                style="background-size: cover;"
            ></div>
            <div class="information flex flex-col gap-2 mr-4">
                <span id="name" class="text-8 text-stone-800 font-[Inter]">
                    Derin Onder Eren
                </span>

                <span
                    id="availability"
                    class="text-6 text-stone-500 font-[Inter] font-light font-italic"
                >
                    available
                </span>

                <span id="links" class="flex gap-4">
                    <a
                        href="https://linkedin.com/in/d3r1n"
                        id="linkedin"
                        class={joinClasses([linkStyle, colorsLinkedin])}
                        innerHTML={LinkedIn}
                    />
                    <a
                        href="https://github.com/d3r1n"
                        id="github"
                        class={joinClasses([linkStyle, colorsGithub])}
                        innerHTML={GitHub}
                    />
                    <a
                        href="https://dev.to/d3r1n"
                        id="devto"
                        class={joinClasses([linkStyle, colorsDevto])}
                        innerHTML={Link}
                    />
                </span>
            </div>
        </div>
    );
}
