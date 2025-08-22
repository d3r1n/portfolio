<script lang="ts">
    import SidebarWidget from "@/lib/main_page/sidebarWidget.svelte";
    import Origins from "@/lib/main_page/origins.svelte";
</script>

<svelte:head>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link
        rel="preconnect"
        href="https://fonts.gstatic.com"
        crossorigin="anonymous"
    />
    <link
        href="https://fonts.googleapis.com/css2?family=Geist:wght@100..900&family=Limelight&family=Nunito:ital,wght@0,200..1000;1,200..1000&display=swap"
        rel="stylesheet"
    />
</svelte:head>

<!-- Outside full width -->
<div class="flex flex-col items-center justify-center gap-16 max-w-full">
    <!-- Content -->
    <div class="flex items-start gap-8 w-full md:max-w-384 p-4">
        <SidebarWidget />

        <div class="flex flex-col gap-16">
            <Origins />
        </div>
    </div>
</div>
