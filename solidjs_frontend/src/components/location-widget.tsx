//@ts-ignore
import apiConfig from "@root/api.const.toml"

const currentLocationUrl = apiConfig.location.baseUrl + apiConfig.location.currentLocationUrl

export default function LocationWidget() {
    return (
        <div class="location-widget relative size-76 p-4 bg-neutral-200 rounded-md">
            <img src={currentLocationUrl} class="w-full h-full rounded-md" />
            <div class="absolute m-4 inset-0 bg-gradient-to-tr from-neutral-200 from-10% to-trasparent to-100% z-1"></div>
            <span class="absolute flex flex-col justify-center items-center left-0 bottom-0 w-full h-full">
                <span class="rounded-full flex size-16 p-1 bg-green-500/60 z-5 mb-4 overflow-hidden">
                    <img class="rounded-full p-[2px] bg-white" src="https://media.licdn.com/dms/image/v2/D4E03AQHbxxIq32jpnA/profile-displayphoto-shrink_400_400/B4EZWyBb5tHMAg-/0/1742448476311?e=1748476800&v=beta&t=_ISJttfHxu51XyzZyBelLo8H7IZ2S9DgkffssWrEFpo" />
                </span>

                <span class="rounded-1/1 animate-ping size-3 bg-green-500/60 mb-1/3"></span>
            </span>
            <span class="location-details absolute flex left-0 bottom-0 p-inherit z-2">
                <div class="details-container flex flex-col p-2 gap-1">
                    <span class="font-[Inter] text-sm font-light">Now</span>
                    <span class="font-[Inter] text-lg font-medium">Mount Allison University</span>
                    <span class="font-[Inter] text-base">Sackville, NB</span>
                </div>
            </span>
        </div>
    )
}