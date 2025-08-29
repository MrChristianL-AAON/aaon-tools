<script lang="ts">
    import '../../../app.css';
    import { serialFormStore } from '$lib/stores';
    import valid from '$lib/assets/valid.svg';
    import invalid from '$lib/assets/invalid.svg';

    // Initialize local state
    let serial_form = $state({
        serial_number: "",
        second_serial_number: "",
        match: false,
    });
    
    // Create a derived value for match that requires non-empty values
    $effect(() => {
        serial_form.match = 
            serial_form.serial_number !== "" &&
            serial_form.second_serial_number !== "" &&
            serial_form.serial_number === serial_form.second_serial_number;
    });

    // Update the store whenever local state changes
    $effect(() => {
        serialFormStore.set(serial_form);
    });

    let matching_image = $derived(serial_form.match ? valid : invalid);

</script>


<main class="box-border p-4 sm:p-5 w-full h-full bg-card-background rounded-2xl sm:rounded-3xl shadow-lg">

    <h1 class="text-xl sm:text-2xl font-bold mb-1 text-dark-text">Serial Number</h1>
    <p class="text-sm sm:text-base text-light-text">Input the serial number of the user's Stratus device. This ensures the commands packages are only compatible with each individual user.</p>    
    
    <div class="mt-6 sm:mt-8">
        <p class="text-sm sm:text-base text-dark-text mb-2">Input unit serial number</p>
        <div class="flex items-center">
            <div class="flex-1">
                <input
                    class="w-full bg-input-background border border-input-border rounded-md p-2 text-sm sm:text-base"
                    type="text"
                    bind:value={serial_form.serial_number}
                    placeholder="Serial Number"
                />
            </div>
            <img class="ml-2 sm:ml-3 w-6 h-6" src={matching_image} alt="Validation status" />
        </div>
    </div>

    <div class="mt-4 sm:mt-6">
        <p class="text-sm sm:text-base text-dark-text mb-2">Confirm unit serial number</p>
        <div class="flex items-center">
            <div class="flex-1">
                <input
                    class="w-full bg-input-background border border-input-border rounded-md p-2 text-sm sm:text-base"
                    type="text"
                    bind:value={serial_form.second_serial_number}
                    placeholder="Confirm Serial Number"
                />
            </div>
            <img class="ml-2 sm:ml-3 w-6 h-6" src={matching_image} alt="Validation status" />
        </div>
    </div>

</main>