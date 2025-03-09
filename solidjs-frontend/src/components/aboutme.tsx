// @ts-ignore
export default function Aboutme(props) {
    return (
        <div
            class={[
                "about-me flex flex-col gap-4 justify-center",
                props.classExtra,
            ].join(" ")}
        >
            <span class="title text-10 font-[Inter]"> About </span>

            <div class="content flex justify-between">
                <div class="basis-6/10 border-stone-200 border-solid border-2 border-rd-md shadow-md flex items-center justify-center">
                    <p class="text-stone-800 font-[Inter] text-lg m-2">
                        I'm Derin, currently pursuing a
                        <i> BSc in Computer Science </i>
                        and a <i>BComm</i> at <b>Mount Allison University.</b> I
                        see myself as a generalist—I follow what interests me,
                        whether it's hardware or software, games or systems,
                        sciences or philosophy. I try to create as much as I
                        consume, always learning or building something new. I
                        built this portfolio as a digital snapshot of who I
                        am—like an online business card of sorts. I'm open to
                        work, collaboration, contributing to projects, or just
                        having a good conversation. Feel free to reach out!
                    </p>
                </div>
                <div class="basis-3/10 flex items-center justify-center bg-stone-100 border-rd-md p-2">
                    <i class="text-center font-[Inter] font-light text-5">
                        "Jack of all trades, master of none, but oftentimes
                        better than master of one."
                    </i>
                </div>
            </div>
        </div>
    );
}
