import { MetaProvider, Link } from "@solidjs/meta";

import Profile from "@/components/profile";
import Aboutme from "@/components/aboutme";
import Navbar from "@/components/navbar";
import SpotifyWidget from "@/components/spotify-widget";

import "../styles/body.css";

export default function Home() {
	return (
		<div class="w-screen h-screen flex flex-col items-center">
			<MetaProvider>
				<Link rel="preconnect" href="https://rsms.me/" />
				<Link rel="stylesheet" href="https://rsms.me/inter/inter.css" />
			</MetaProvider>

			<Navbar classExtra={["mt-4"]} />
			<div class="page-content flex flex-col items-center w-full mt-28 gap-8">
				<Profile classExtra={["w-8/10"]} />
				<Aboutme classExtra={["w-8/10"]} />
			</div>
		</div>
	);
}
