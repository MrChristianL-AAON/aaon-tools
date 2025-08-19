<script lang="ts">
    import '../app.css';

let serial_form = $state({
    serial_number: "",
    second_serial_number: "",
    match: false,
});

let matching_image = $derived(serial_form.match ? valid : invalid);

import valid from '$lib/assets/valid.svg';
import invalid from '$lib/assets/invalid.svg';

</script>


<main class="box-border p-5 w-full h-88 max-w-115 bg-card-background rounded-3xl shadow-lg">

    <h1 class="text-2xl font-bold mb-1 text-dark-text">Serial Number</h1>
    <p class="text-light-text">Input the serial number of the user's Stratus device. This ensures the commands packages are only compatible with each individual user.</p>    
    <p class="pt-10 text-dark-text">Input unit serial number</p>
    
    <div class="flex items-center ">
        <div>
            <input
                class ="w-85 bg-input-background border border-input-border rounded-md p-2"
                type="text"
                bind:value={serial_form.serial_number}
                placeholder="Serial Number"
            />
        </div>
        <img class="ml-3" src={matching_image} alt="" />
    </div>

    <div class="flex items-center pt-8">
        <div>
            <p class="text-dark-text">Confirm unit serial number</p>
            <input
                class ="w-85 bg-input-background border border-input-border rounded-md p-2 mb-4"
                type="text"
                bind:value={serial_form.second_serial_number}
                placeholder="Confirm Serial Number"
                oninput={() => {
                    serial_form.match = serial_form.serial_number === serial_form.second_serial_number;
                }}
            />
        </div>
        <img class="ml-3 pt-2" src={matching_image} alt="" />

    </div>

</main>