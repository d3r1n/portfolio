let navbar_style = "nav-button flex justify-center text-center text-stone-950";

export default function Navbar() {
    return (
        <div class="navbar w-full border-b-dotted border-b-3 border-gray-300">
            <div class="navbar-inner flex items-center justify-between font-[Inter] p-2 border-rd-sm bg-gray-100 text-lg mb-2">
                <span
                    id="left-side"
                    class={navbar_style + " tracking-wider ml-4 select-none"}
                >
                    d3r1noe
                </span>

                <div id="right-side" class="flex items-center gap-5 mr-4">
                    <span class={navbar_style}>
                        <a href="#about" class="no-underline text-stone-950">
                            About
                        </a>
                    </span>

                    <span class={navbar_style}>
                        <a href="#projects" class="no-underline text-stone-950">
                            Projects
                        </a>
                    </span>
                </div>
            </div>
        </div>
    );
}
