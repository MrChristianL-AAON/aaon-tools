<script lang="ts">
    import Cloud from '$lib/assets/cloud.svg';
    import CloudDark from '$lib/assets/cloud-dark.svg';
    import { goto } from '$app/navigation';

    export let path = '/update_archives';
    export let title = 'Update Archives';
    export let description = 'Click here to access official and developmental releases of update packages for the Stratus Unit Manager.';

    let imgSrc = CloudDark;
    let imgAlt = "Update Archives Icon";

    // Fluid responsive text styles with better scaling across screen sizes
    let titleStyle = "text-lg sm:text-xl md:text-2xl font-semibold text-dark-text mt-2 sm:mt-3";
    let descStyle = "mt-1 sm:mt-2 text-center text-xs sm:text-sm text-dark-text";

    function handleMouseOverOrFocus() {
        imgSrc = Cloud;
        titleStyle = "text-lg sm:text-xl md:text-2xl font-semibold text-card-background mt-2 sm:mt-3";
        descStyle = "mt-1 sm:mt-2 text-center text-xs sm:text-sm text-card-background";
    }

    function handleMouseOutOrBlur() {
        imgSrc = CloudDark;
        titleStyle = "text-lg sm:text-xl md:text-2xl font-semibold text-dark-text mt-2 sm:mt-3";
        descStyle = "mt-1 sm:mt-2 text-center text-xs sm:text-sm text-dark-text";
    }
</script>

<div class="h-full w-full">
    <button
        class="w-full h-full min-h-[200px] flex flex-col items-center justify-center bg-card-background rounded-lg shadow-lg hover:bg-aaon-blue-light p-3 sm:p-4 md:p-6 cursor-pointer transition-all duration-200"
        onclick={() => {
            goto(path);
        }}
        onmouseover={handleMouseOverOrFocus}
        onfocus={handleMouseOverOrFocus}
        onmouseout={handleMouseOutOrBlur}
        onblur={handleMouseOutOrBlur}
        aria-label={title}
    >
        <div class="flex flex-col items-center justify-center h-full w-full py-2 sm:py-4">
            <img  
                class="h-6 sm:h-8 md:h-10 w-auto object-contain"
                src={imgSrc}
                alt={imgAlt}
            />
            <span class={titleStyle}>
                {title}
            </span>
            <span class={descStyle}>
                <p class="max-w-[90%] mx-auto">
                    {description}
                </p>
            </span>
        </div>
    </button>       
</div>