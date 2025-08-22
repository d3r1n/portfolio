<script lang="ts">
    type InProgressListType = {
        action: string;
        description: string;
        link?: string;
    };

    // TODO: make it into a backend request and make it server side rendered.
    // make it into a dashboardy-thing for being able to update what I'm doing
    const inProgressList: InProgressListType[] = [
        {
            action: "Learning",
            description: "Rust, C, low level programming & system design.",
        },
        {
            action: "Studying",
            description: "Calculus, linear algebra and more math concepts.",
        },
        {
            action: "Developing",
            description: "Konfigur, platform agnostic configuration manager.",
        },
        {
            action: "Thinkering",
            description: "Engineering, computer aided design, mechatronics.",
        },
    ];
</script>

<div class="flex flex-col gap-4">
    <h1 class="font-[LimeLight] text-4xl tracking-wide text-base-content">
        ORIGINS
    </h1>

    <!-- Personal Statement Part -->
    <div class="flex flex-col gap-4 mb-4">
        <p
            class="font-[Geist] text-lg text-base-content [&_span]:tooltip [&_span]:text-primary [&_span]:underline [&_span]:decoration-dotted"
        >
            My name is Derin. If you ask me who <i>Derin</i> is, I could give
            you coordinates: where I was
            <span data-tip="Istanbul/Turkey"> born </span>
            , where I
            <span data-tip="actively looking for an internship"> work </span>
            . I could list the
            <span data-tip="Mount Allison University"> university </span>
            I'm attending, names of the
            <span data-tip="BSc Computer Science & Commerce"> programs </span>
            I'm studying... These are surface level details. But none of that will
            bring you closer to who I actually am. So let's save the
            <span
                class="!tooltip-none !no-underline bg-gradient-to-r from-amber-500 to-pink-500 bg-clip-text !text-transparent font-bold"
            >
                bullsh*t brûlée
            </span>
            for someone with sweeter tooth.
        </p>

        <p class="font-[Geist] text-lg text-base-content">
            I don't have a five-year blueprint. I have questions that burn,
            ideas that glow, and dreams that fuel me. I build what wasn't there
            before - create uniqueness - not for interference, but because I
            just can't not. Labels are too tight. I live at intersections: STEM,
            art, music, poetry, logic, curiosity, chaos, calm. I'm not built for
            one lane; I move through disciplines like they're languages, not
            borders. Because borders bore me. Get it? Lastly here's a quote that
            I live by:
        </p>

        <div
            class="flex items-center gap-4 font-[Nunito] text-lg text-base-content italic"
        >
            <span class="w-1 h-8 bg-base-200 rounded-full"></span>
            "Jack of all trades, master of none. Most times better than master of
            one."
        </div>

        <p class="font-[Geist] text-lg text-base-content">
            In short? I am a dreamer. A thinker. A doer.
        </p>
    </div>

    <div class="flex"></div>
</div>
