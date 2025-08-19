<script lang="ts">

import JsonFile from "./json_file.svelte";
import SerialNumber from "./serial_number.svelte";

let responsive = $derived(
    {
        // JsonFile.json_file,
        // SerialNumber.serial_form.match
        // This is a placeholder for de-graying out the button when the pre-reqs have yet to be met
    });

</script>

<main class="items-center">
    <button>
        <div class="flex items-center justify-center w-52 bg-aaon-blue text-white text-2xl font-semibold py-2 px-4 shadow-lg hover:bg-aaon-blue-light rounded-lg transition-colors duration-300 cursor-pointer">
            Initiate Build
        </div>
    </button>
</main>