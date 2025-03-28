const buttonClass =
	"nav-button px-8 py-2 bg-transparent hover:bg-blue-400:25 active:bg-blue-500 transition border-solid border-2 border-blue-500 rounded-md font-[Inter} text-lg font-normal text-blue-500 active:text-neutral-100";

//@ts-ignore
export default function Navbar(props) {
	return (
		<div
			class={[
				"container flex w-full justify-center z-10",
				...props.classExtra,
			].join(" ")}
		>
			<div class="navbar box-border fixed flex justify-between items-center w-95/100 px-8 py-4 bg-neutral-200/50 border-solid border-1 border-neutral-800/25 rounded-md backdrop-blur-sm shadow-md hover:shadow-lg transition">
				<span class="site-name text-xl font-[Inter] tracking-widest">
					derineren.net
				</span>

				<span class="navigations flex justify-between items-center gap-4">
					<button class={buttonClass}>About</button>
					<button class={buttonClass}>Projects</button>
					{/* TODO: theme toggle */}
				</span>
			</div>
		</div>
	);
}
