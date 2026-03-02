export const theme = $state({
	current: "wireframe",
	toggle() {
		this.current = this.current === "wireframe" ? "black" : "wireframe";
		localStorage.setItem("theme", this.current);
		document.documentElement.setAttribute("data-theme", this.current);
	},
});
