import LinkedIn from "iconoir/icons/regular/linkedin.svg?raw";
import GitHub from "iconoir/icons/regular/github.svg?raw";
import Link from "iconoir/icons/regular/link.svg?raw";

const linkStyle =
	"link *:size-8 p-1 flex border-solid border-2 rounded-md color-neutral-600 hover:bg-neutral-600 hover:color-neutral-100 hover:border-neutral-600 transition";

const buttonStyle =
	"button px-4 py-2 text-center text-lg text-neutral-100 border-none rounded-md bg-blue-500 hover:bg-blue-400 transition";

const taglines = [
	"jack of all trades",
	"too many ideas, not enough hours",
	"not normal, quite the opposite",
	"let's go invent tomorrow...",
];

function random_tagline() {
	return taglines[Math.floor(Math.random() * taglines.length)];
}

// @ts-ignore
export default function Profile(props) {
	return (
		<div
			class={["profile flex justify-between", ...props.classExtra].join(" ")}
		>
			<div class="profile-details flex flex-col gap-4 justify-center items-center w-max">
				<span
					id="tagline"
					class="font-[Inter] font-light italic text-xl text-neutral-600 text-center w-full"
				>
					{random_tagline()}
				</span>

				<span
					id="name"
					class="font-[Inter] font-medium text-4xl text-neutral-800 text-center w-full"
				>
					Derin Önder EREN
				</span>

				<div class="socials w-full flex gap-4 justify-center items-center">
					<a href="" class={linkStyle} innerHTML={LinkedIn}></a>
					<a href="" class={linkStyle} innerHTML={GitHub}></a>
					<a href="" class={linkStyle} innerHTML={Link}></a>
				</div>

				<div class="actions w-full font-[Inter] flex gap-4 justify-center items-center">
					<button class={buttonStyle}>contact me</button>
					<button class={buttonStyle}>view projects</button>
				</div>
			</div>

			<div class="profile-image">
				<img
					class="rounded-md"
					src="https://media.licdn.com/dms/image/v2/D4E03AQHbxxIq32jpnA/profile-displayphoto-shrink_400_400/B4EZWyBb5tHMAg-/0/1742448476311?e=1748476800&v=beta&t=_ISJttfHxu51XyzZyBelLo8H7IZ2S9DgkffssWrEFpo"
					alt=""
				/>
			</div>
		</div>
	);
}
