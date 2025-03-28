import SpotifyWidget from "./spotify-widget";

// @ts-ignore
export default function Aboutme(props) {
	return (
		<div class={["about flex flex-col gap-4", ...props.classExtra].join(" ")}>
			<span class="about-title font-[Inter] text-3xl text-neutral-700">
				About
			</span>

			<div class="about-content grid grid-cols-3 grid-rows-2 gap-8 w-full">
				<span class="about-text	col-span-2 flex justify-center align-center p-4 rounded-md bg-neutral-200 font-[Inter] text-lg text-neutral-900">
					<p class="p-0 m-0 h-max">
						I'm Derin, currently pursuing a <i>BSc in Computer Science </i>
						and a <i> BComm </i> at <b> Mount Allison University. </b>I consider
						myself a generalist—I follow my curiosity, whether it leads me to
						hardware or software, games or systems, sciences or philosophy. I
						aim to create as much as I consume, always learning or building
						something new.
						<br />
						This portfolio serves as a digital snapshot of who I am—like an
						online business card. I'm open to work, collaboration, contributing
						to projects, or simply having a great conversation. Feel free to
						reach out!
					</p>
				</span>

				<SpotifyWidget />

				<span class="about-location_widget"></span>

				<span class="about-fun_facts cols-span-2"></span>
			</div>
		</div>
	);
}
