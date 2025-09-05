<script lang="ts">
    import Cloud from '$lib/assets/cloud.svg';
    import CloudDark from '$lib/assets/cloud-dark.svg';
    import { goto } from '$app/navigation';

    let imgSrc = CloudDark;
    let imgAlt = "Update Builder Icon";

    let titleStyle = "text-2xl font-semibold text-dark-text mt-4";
    let descStyle = "mt-2 text-center text-sm text-dark-text";

    function handleMouseOverOrFocus() {
        imgSrc = Cloud;
        titleStyle = "text-2xl font-semibold text-card-background mt-4";
        descStyle = "mt-2 text-center text-sm text-card-background";
    }

    function handleMouseOutOrBlur() {
        imgSrc = CloudDark;
        titleStyle = "text-2xl font-semibold text-dark-text mt-4";
        descStyle = "mt-2 text-center text-sm text-dark-text";
    }
</script>

<main>
    <div>
        <button
            class="w-120 h-80 items-center justify-center bg-card-background rounded-lg shadow-lg hover:bg-aaon-blue-light p-4 cursor-pointer"
            onclick={() => {
                goto('/update_archives');
            }}
            onmouseover={handleMouseOverOrFocus}
            onfocus={handleMouseOverOrFocus}
            onmouseout={handleMouseOutOrBlur}
            onblur={handleMouseOutOrBlur}
        >
            <div class="flex flex-col items-center justify-center">
                <img  
                    class="h-8 md:h-10 w-auto object-contain"
                    src={imgSrc}
                    alt={imgAlt}
                />
                <span class={titleStyle}>
                    Update Archives
                </span>
                <span class={descStyle}>
                    <p>
                        Click here to access official and developmental releases update packages for the Stratus Unit Manager.
                    </p>
                </span>
            </div>
        </button>       
    </div>
</main>