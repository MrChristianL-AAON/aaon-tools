import { writable } from 'svelte/store';

// Store for serial number state
export const serialFormStore = writable<{
    serial_number: string,
    second_serial_number: string,
    match: boolean
}>({
    serial_number: "",
    second_serial_number: "",
    match: false
});

// Store for JSON file state
export const jsonFileStore = writable<{
    file: File | null
}>({
    file: null
});


export const debFiles = writable<File[]>([]);
